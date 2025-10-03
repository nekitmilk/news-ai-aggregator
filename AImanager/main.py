import json
import redis
import pika
import logging
import threading
import time
from queue import Queue
from manager import SummarizerManager
from categorizer_manager import CategorizerManager
import uuid

logger = logging.getLogger("NewsConsumer")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class NewsConsumer:
    def __init__(self, conf: dict):
        self.conf = conf

        # --- Redis ---
        self.redis_client = redis.StrictRedis(
            host=conf['redis']['host'],
            port=conf['redis']['port'],
            db=conf['redis'].get('db', 0),
            decode_responses=True
        )
        logger.info("✅ Подключение к Redis успешно")

        # --- Summarizer и Categorizer ---
        self.summarizer_manager = SummarizerManager(device=0)
        self.categorizer_manager = CategorizerManager(device=0)

        # --- RabbitMQ ---
        self.connect_rabbitmq()

    def connect_rabbitmq(self):
        """Подключение к RabbitMQ с retry"""
        while True:
            try:
                self.rabbit_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.conf['rabbitmq']['host'],
                        port=self.conf['rabbitmq'].get('port', 5672),
                        credentials=pika.PlainCredentials(
                            self.conf['rabbitmq']['user'],
                            self.conf['rabbitmq']['password']
                        ),
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.rabbit_connection.channel()

                # Основные очереди
                self.queue_name = self.conf['rabbitmq']['queue']
                self.processed_queue_name = self.conf['rabbitmq'].get('processed_queue', 'processed_news')
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                self.channel.queue_declare(queue=self.processed_queue_name, durable=True)
                self.channel.basic_qos(prefetch_count=1)

                # Подписка на очередь
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self.callback,
                    auto_ack=False
                )

                logger.info("✅ Подключение к RabbitMQ успешно")
                break
            except Exception as e:
                logger.warning(f"⚠️ Не удалось подключиться к RabbitMQ: {e}, повтор через 5 сек")
                time.sleep(5)

    def start_consuming(self):
        logger.info("🚀 Консюмер запущен. Ожидание сообщений...")
        while True:
            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                logger.info("🛑 Консюмер завершает работу.")
                break
            except (pika.exceptions.StreamLostError, pika.exceptions.ConnectionClosed, pika.exceptions.AMQPConnectionError) as e:
                logger.warning(f"⚠️ Соединение с RabbitMQ потеряно: {e}, переподключаемся...")
                self.connect_rabbitmq()

    def callback(self, ch, method, properties, body):
        key = body.decode('utf-8')
        news_json_raw = self.redis_client.get(key)
        if not news_json_raw:
            logger.warning(f"⚠️ Ключ '{key}' не найден в Redis")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        news_data = json.loads(news_json_raw)
        text = news_data.get('text', "")

        if not text.strip():
            logger.warning("⚠️ Текст новости пустой, суммаризация пропущена")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Очередь для результата из потока
        result_queue = Queue()

        def process_in_thread():
            try:
                # --- Summarization ---
                summary, sum_duration = self.summarizer_manager.summarize(text)
                logger.info(f"[SUMMARY]: {summary}")
                logger.info(f"⏱ Время суммаризации: {sum_duration:.2f} сек")

                # --- Categorization ---
                categories, cat_duration = self.categorizer_manager.categorize(summary)
                best_cat = categories[0]["label"] if categories else "другое"
                score = categories[0]["score"] if categories else 0.0
                logger.info(f"[CATEGORY]: {best_cat} (score={score:.2f})")
                logger.info(f"⏱ Время категоризации: {cat_duration:.2f} сек")

                # --- Формируем JSON ---
                processed_news = {
                    "id": str(uuid.uuid4()),
                    "title": news_data.get('header', ''),
                    "summary": summary,
                    "category": best_cat,
                    "source": news_data.get('source_name', ''),
                    "url": news_data.get('url', ''),
                    "date": news_data.get('date', '')
                }

                result_queue.put(("success", processed_news))
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке текста: {e}", exc_info=True)
                result_queue.put(("error", None))

        # Запуск потока для обработки
        thread = threading.Thread(target=process_in_thread)
        thread.start()

        # Поддержка heartbeat во время обработки
        while thread.is_alive():
            try:
                self.rabbit_connection.process_data_events(time_limit=1)
            except Exception as e:
                logger.warning(f"⚠️ Ошибка в process_data_events: {e}")
            time.sleep(0.1)

        thread.join()

        # Получаем результат
        status, processed_news = result_queue.get()

        if status == "error":
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Отправка в processed_queue
        self.send_to_processed_queue(processed_news, ch)

        # Ack
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_to_processed_queue(self, news_json: dict, ch):
        """Отправка обработанной новости с переподключением"""
        while True:
            try:
                ch.basic_publish(
                    exchange='',
                    routing_key=self.processed_queue_name,
                    body=json.dumps(news_json),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                logger.info(f"📤 Новость отправлена в очередь '{self.processed_queue_name}'")
                break
            except (pika.exceptions.ChannelWrongStateError,
                    pika.exceptions.StreamLostError,
                    pika.exceptions.ConnectionClosed) as e:
                logger.warning(f"⚠️ Соединение потеряно при отправке: {e}, переподключаемся...")
                self.connect_rabbitmq()
                ch = self.channel  # Обновляем канал после переподключения


if __name__ == "__main__":
    with open("config.json", 'r', encoding='utf-8') as file:
        conf = json.load(file)

    consumer = NewsConsumer(conf)
    consumer.start_consuming()