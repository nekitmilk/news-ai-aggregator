import json
import logging
import asyncio
from typing import Dict, Any
from urllib.parse import urlparse
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from sqlmodel import Session, select
from datetime import datetime

from app.core.config import settings
from app.core.db import engine
from app.models import ProcessedNews, Source, Category

logger = logging.getLogger(__name__)

class NewsConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.is_connected = False
        self.reconnect_delay = settings.RABBITMQ_RECONNECT_DELAY  # seconds
        self.is_running = True
    
    async def connect(self):
        """Простое подключение к RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                timeout=10
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            
            # Подключаемся к существующей очереди
            self.queue = await self.channel.get_queue(
                settings.RABBITMQ_PROCESSED_NEWS_QUEUE
            )
            
            if self.queue is None:
                raise ConnectionError(f"Queue {settings.RABBITMQ_PROCESSED_NEWS_QUEUE} not found")
            
            self.is_connected = True
            logger.info("✅ Successfully connected to RabbitMQ")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.is_connected = False
            return False
    
    async def wait_for_connection(self):
        """Ожидание восстановления подключения"""
        while self.is_running and not self.is_connected:
            logger.info(f"🔄 Waiting for RabbitMQ... (retry in {self.reconnect_delay}s)")
            await asyncio.sleep(self.reconnect_delay)
            
            if await self.connect():
                return True
        
        return False
    
    async def start_consuming(self):
        """Запуск потребителя с бесконечным ожиданием подключения"""
        while self.is_running:
            if not self.is_connected:
                # Ждем пока подключение не восстановится
                if not await self.wait_for_connection():
                    continue
            
            try:
                # Начинаем потребление сообщений
                await self.queue.consume(self.process_message)
                logger.info("🎯 Started consuming messages from RabbitMQ")
                
                # Ждем пока соединение активно
                await asyncio.Future()  # Бесконечное ожидание
                
            except asyncio.CancelledError:
                logger.info("Consumer was cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Connection lost: {e}")
                self.is_connected = False
                await self.disconnect()
    
    async def process_message(self, message: AbstractIncomingMessage):
        """Обработка входящего сообщения"""
        try:
            async with message.process():
                news_data = json.loads(message.body.decode())
                logger.info(f"📨 Processing: {news_data.get('title')}")
                await self.save_processed_news(news_data)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
    
    async def save_processed_news(self, news_data: Dict[str, Any]):
        """Сохранение новости в БД"""
        try:
            with Session(engine) as session:
                title = news_data.get("title", "").strip()

                published_date = news_data.get("published_date", "")
                if not published_date:
                    published_date = datetime.now()

                summary=news_data.get("summary", "").strip()
                
                if not title or not summary:
                    logger.error("Missing required fields")
                    return
                
                # Проверяем дубликат по URL
                existing = session.exec(
                    select(ProcessedNews).where(ProcessedNews.url == news_data.get("url", ""))
                ).first()
                if existing:
                    logger.info(f"⚠️ News already exists: {title}")
                    return
                
                source_name = news_data.get("source_name", "Unknown Source").strip()
                source_url = news_data.get("url", "").strip()
                source_domain = self.extract_domain(source_url)
                
                source = await self.get_or_create_source(session, source_name, source_domain)
                category = await self.get_or_create_category(session, news_data.get("category", "general").strip())
                
                db_news = ProcessedNews(
                    title=title,
                    summary=summary,
                    url=source_url,
                    published_at=published_date,
                    source_id=source.id,
                    category_id=category.id
                )
                
                session.add(db_news)
                session.commit()
                logger.info(f"✅ Saved: {title}")
                
        except Exception as e:
            logger.error(f"❌ Save error: {e}")
    
    def extract_domain(self, url: str) -> str:
        """Извлекает домен из URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain if domain else "unknown-domain"
        except Exception:
            return "unknown-domain"
    
    async def get_or_create_source(self, session: Session, name: str, domain: str) -> Source:
        statement = select(Source).where(Source.name == name)
        source = session.exec(statement).first()
        if not source:
            source = Source(name=name, domain=domain)
            session.add(source)
            session.commit()
            session.refresh(source)
            logger.info(f"📝 Created source: {name}")
        return source
    
    async def get_or_create_category(self, session: Session, name: str) -> Category:
        statement = select(Category).where(Category.name == name)
        category = session.exec(statement).first()
        if not category:
            category = Category(name=name)
            session.add(category)
            session.commit()
            session.refresh(category)
            logger.info(f"📝 Created category: {name}")
        return category
    
    async def disconnect(self):
        """Корректное отключение"""
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            logger.info("🔌 Disconnected from RabbitMQ")
    
    async def stop(self):
        """Остановка потребителя"""
        self.is_running = False
        await self.disconnect()
        logger.info("🛑 Consumer stopped")

# Глобальный экземпляр
news_consumer = NewsConsumer()