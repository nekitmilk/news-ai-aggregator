import time
import json
import random
import asyncio
import schedule
import threading
import redis
import pika
from fake_useragent import UserAgent
from datetime import datetime
from parser import Parser

class RunParser:
    def __init__(self, conf: dict, random_user_agent: bool = True):
        self.conf = conf
        self.conf['parser']['headers']['User-Agent'] = UserAgent().random if random_user_agent \
            else self.conf['parser']['headers']['User-Agent']

        self.parser: Parser = Parser(
            headers=self.conf["parser"]["headers"],
            resources=self.conf["parser"]["resources"],
        )

        self.redis_client = redis.StrictRedis(
            host=self.conf["redis"]["host"],
            port=self.conf["redis"]["port"],
            db=self.conf["redis"].get("db", 0),
            decode_responses=True
        )

        self.rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.conf["rabbitmq"]["host"],
                port=self.conf["rabbitmq"].get("port", 5672),
                credentials=pika.PlainCredentials(
                    self.conf["rabbitmq"]["user"],
                    self.conf["rabbitmq"]["password"]
                )
            )
        )
        self.rabbit_channel = self.rabbit_connection.channel()
        self.rabbit_channel.queue_declare(queue=self.conf["rabbitmq"]["queue"], durable=True)

    def run(self):
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Основная программа завершается.")
            schedule.clear()

    def _write_resource_news(self, resource):
        try:
            rabbit_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.conf["rabbitmq"]["host"],
                    port=self.conf["rabbitmq"].get("port", 5672),
                    credentials=pika.PlainCredentials(
                        self.conf["rabbitmq"]["user"],
                        self.conf["rabbitmq"]["password"]
                    )
                )
            )
            rabbit_channel = rabbit_connection.channel()
            rabbit_channel.queue_declare(queue=self.conf["rabbitmq"]["queue"], durable=True)

            news = asyncio.run(self.parser.get_news(resource, limit=self.conf['parser']['news_limit']))
            for n in news:
                n["source"] = resource
                n["source_type"] = "telegram" if "t.me" in n.get("url", "") else "rss"
                header_key = n["header"]

                if self.redis_client.exists(header_key):
                    print(f"[SKIP] {resource}: новость '{header_key}' уже существует в Redis, пропускаем")
                    continue

                news_json = json.dumps(n, ensure_ascii=False, indent=4, default=json_serializer)
                self.redis_client.set(header_key, news_json)

                if self.redis_client.exists(header_key):
                    rabbit_channel.basic_publish(
                        exchange="",
                        routing_key=self.conf["rabbitmq"]["queue"],
                        body=header_key,
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    print(f"[OK] {resource}: новость '{header_key}' сохранена в Redis и отправлена в RabbitMQ")
                else:
                    print(f"[ERR] {resource}: не удалось сохранить новость '{header_key}' в Redis")

            rabbit_connection.close()

        except Exception as e:
            raise Exception(f"write_resource_news:{resource}: {e}")

    def _run_scheduler(self):
        base_interval = self.conf['parser']['periodicity']
        
        for resource in self.parser.resources:
            variance = base_interval * 0.3
            interval = base_interval + random.uniform(-variance, variance)
            
            def job(r=resource):
                self._run_parser_in_thread(r)
            
            self._run_parser_in_thread(resource)
            schedule.every(round(interval)).minutes.do(job)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def _run_parser_in_thread(self, resource):
        thread = threading.Thread(target=self._write_resource_news,
                                args=(resource,))
        thread.daemon = True
        thread.start()


def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


if __name__ == "__main__":
    with open("config.json", 'r', encoding='utf-8') as file:
        conf = json.load(file)
    
    RunParser(conf).run()
