import json
import redis
import pika
import logging
import threading
from queue import Queue
from manager import SummarizerManager
from categorizer_manager import CategorizerManager  # 👈 добавляем импорт

logger = logging.getLogger("NewsConsumer")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class NewsConsumer:
    def __init__(self, conf: dict):
        self.conf = conf

        self.redis_client = redis.StrictRedis(
            host=conf['redis']['host'],
            port=conf['redis']['port'],
            db=conf['redis'].get('db', 0),
            decode_responses=True
        )
        logger.info("✅ Подключение к Redis успешно")

        self.rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=conf['rabbitmq']['host'],
                port=conf['rabbitmq'].get('port', 5672),
                credentials=pika.PlainCredentials(
                    conf['rabbitmq']['user'],
                    conf['rabbitmq']['password']
                ),
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        self.channel = self.rabbit_connection.channel()
        self.channel.queue_declare(queue=conf['rabbitmq']['queue'], durable=True)
        self.channel.basic_qos(prefetch_count=1)
        logger.info("✅ Подключение к RabbitMQ успешно")

        # --- Summarizer ---
        logger.info("⏳ Загружаем Summarizer на GPU...")
        self.summarizer_manager = SummarizerManager(device=0)
        logger.info("✅ Summarizer загружен")

        # --- Categorizer ---
        logger.info("⏳ Загружаем Categorizer на GPU...")
        self.categorizer_manager = CategorizerManager(device=0)
        logger.info("✅ Categorizer загружен")

        self.model_queue = Queue()
        self.model_thread = threading.Thread(target=self.model_worker, daemon=True)
        self.model_thread.start()

        self.channel.basic_consume(
            queue=conf['rabbitmq']['queue'],
            on_message_callback=self.callback,
            auto_ack=False
        )

    def model_worker(self):
        """Отдельный поток для работы с моделью"""
        while True:
            key, text, ch, method = self.model_queue.get()
            try:
                # --- Summarization ---
                summary, duration = self.summarizer_manager.summarize(text)
                logger.info(f"[SUMMARY]: {summary}")
                logger.info(f"⏱ Время суммаризации: {duration:.2f} сек")

                # --- Categorization ---
                categories, cat_duration = self.categorizer_manager.categorize(summary)
                best_cat = categories[0]["label"] if categories else ""
                score = categories[0]["score"] if categories else 0
                logger.info(f"[CATEGORY]: {best_cat} (score={score:.2f})")
                logger.info(f"⏱ Время категоризации: {cat_duration:.2f} сек")

                # --- Формируем JSON для продюсера ---
                processed_news = {
                    "id": str(uuid.uuid4()),
                    "title": self.redis_client.get(key) and json.loads(self.redis_client.get(key)).get('header', ''),
                    "summary": summary,
                    "category": best_cat,
                    "source": self.redis_client.get(key) and json.loads(self.redis_client.get(key)).get('source_name', ''),
                    "url": self.redis_client.get(key) and json.loads(self.redis_client.get(key)).get('url', ''),
                    "date": self.redis_client.get(key) and json.loads(self.redis_client.get(key)).get('date', '')
                }

                # --- Отправляем в отдельную очередь ---
                self.send_to_processed_queue(processed_news)

                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                logger.error(f"❌ Ошибка при обработке текста: {e}", exc_info=True)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            finally:
                self.model_queue.task_done()

    def send_to_processed_queue(self, news_json: dict):
        """Отправка обработанной новости в отдельную очередь"""
        queue_name = self.conf['rabbitmq'].get('processed_queue', 'processed_news')
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(news_json),
            properties=pika.BasicProperties(
                delivery_mode=2  # сохраняем сообщение при падении сервера
            )
        )
        logger.info(f"📤 Новость отправлена в очередь '{queue_name}'")

    def start_consuming(self):
        logger.info("🚀 Консюмер запущен. Ожидание сообщений...")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("🛑 Консюмер завершает работу.")
        except pika.exceptions.StreamLostError as e:
            logger.warning(f"⚠️ Соединение с RabbitMQ потеряно: {e}, переподключаемся...")
            self.__init__(self.conf)
            self.start_consuming()

    def callback(self, ch, method, properties, body):
        key = body.decode('utf-8')
        logger.info(f"📩 Получен ключ из RabbitMQ: {key}")

        news_json = self.redis_client.get(key)
        if not news_json:
            logger.warning(f"⚠️ Ключ '{key}' не найден в Redis")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        news_data = json.loads(news_json)
        header = news_data.get('header')
        text = news_data.get('text', "")

        logger.info(f"📰 Заголовок: {header}")
        logger.info(f"📅 Дата: {news_data.get('date')}")
        logger.info(f"🔗 URL: {news_data.get('url')}")

        if text.strip():
            try:
                summary, duration = self.summarizer_manager.summarize(text)
                logger.info(f"[SUMMARY]: {summary}")
                logger.info(f"⏱ Время суммаризации: {duration:.2f} сек")

                categories, cat_duration = self.categorizer_manager.categorize(summary)
                if categories:
                    best_cat = categories[0]["label"]
                    score = categories[0]["score"]
                    logger.info(f"[CATEGORY]: {best_cat} (score={score:.2f})")
                logger.info(f"⏱ Время категоризации: {cat_duration:.2f} сек")

            except Exception as e:
                logger.error(f"❌ Ошибка при обработке текста: {e}", exc_info=True)
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logger.warning("⚠️ Текст новости пустой, суммаризация пропущена")
            ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    with open("config.json", 'r', encoding='utf-8') as file:
        conf = json.load(file)

    consumer = NewsConsumer(conf)
    consumer.start_consuming()
