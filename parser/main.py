import os
import time
import json
import random
import asyncio
import schedule
import threading
from datetime import datetime
from parser import Parser

class RunParser:
    def __init__(self, conf: dict):
        self.conf = conf
        self.parser: Parser = Parser(
            headers=self.conf["parser"]["headers"],
            resources=self.conf["parser"]["resources"],
        )

    def write_resource_news(self, resource):
        try:
            news = asyncio.run(self.parser.get_news(resource, limit=self.conf['parser']['news_limit']))
            os.makedirs("data", exist_ok=True)
            with open(f"data/{resource.upper()}-{time.time()}.json", 'w', encoding="utf-8") as file:
                json.dump(news, file,
                        ensure_ascii=False,
                        indent=4,
                        default=json_serializer)
        except Exception as e:
            raise Exception(f"write_resource_news:{resource}: {e}")


    def run_parser_in_thread(self, resource):
        thread = threading.Thread(target=self.write_resource_news,
                                args=(resource,))
        thread.daemon = True
        thread.start()

    def run_scheduler(self):
        base_interval = self.conf['parser']['periodicity']
        
        for resource in self.parser.resources:
            variance = base_interval * 0.3
            interval = base_interval + random.uniform(-variance, variance)
            
            def job(r=resource):
                self.run_parser_in_thread(r)
            
            self.run_parser_in_thread(resource)
            schedule.every(round(interval)).minutes.do(job)

        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def run(self):
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Основная программа завершается.")
            schedule.clear()

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

if __name__ == "__main__":
    with open("config.json", 'r', encoding='utf-8') as file:
        conf = json.load(file)
    
    RunParser(conf).run()
