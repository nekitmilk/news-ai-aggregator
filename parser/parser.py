import re
import asyncio
import feedparser
from newspaper import Article
from datetime import datetime
from telethon import TelegramClient

class Parser:
    def __init__(self, headers: dict = None, resources: dict = None):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.resources = resources or {}

    async def get_news(self, resource: str, limit: int = 10) -> list[dict]:
        if resource not in self.resources:
            raise ValueError(f"get_news:{resource} не найден в конфигурации")

        config = self.resources[resource]
        news_data = []

        try:
            if 'rss' in config:
                news_data = await self._parse_rss_news(resource, limit)
            else:
                raise ValueError(f"get_news:Для {resource} не указан RSS")
            return news_data[:limit]

        except Exception as e:
            raise Exception(f"get_news:{resource}: {e}")

    async def _parse_rss_news(self, resource: str, limit: int) -> list[dict]:
        config = self.resources[resource]
        feed = feedparser.parse(config['rss'], request_headers=self.headers)
        
        tasks = []
        for entry in feed.entries[:limit]:
            tasks.append(self._parse_news_article(entry.link))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        news_data = [result for result in results if isinstance(result, dict)]
        return news_data

    async def _parse_news_article(self, url: str):
        try:
            loop = asyncio.get_event_loop()
            article_data = await loop.run_in_executor(None, self._parse_article_sync, url)
            
            if not article_data or not article_data.get('header'):
                return None

            return {
                'header': article_data['header'],
                'text': article_data['text'],
                'date': article_data['date'],
                'url': url
            }

        except Exception as e:
            print(f"_parse_news_article:{url}: {e}")
            return None

    def _parse_article_sync(self, url: str):
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if not article.title or not article.text:
                return None

            publish_date = self._extract_publication_date(article, url)
            
            return {
                'header': article.title,
                'text': article.text,
                'date': publish_date
            }

        except Exception as e:
            print(f"_parse_article_sync:{url}: {e}")
            return None

    def _extract_publication_date(self, article, url: str) -> datetime:
        if article.publish_date:
            return article.publish_date
        
        meta_date = self._extract_date_from_meta(article)
        if meta_date:
            return meta_date
        
        url_date = self._extract_date_from_url(url)
        if url_date:
            return url_date
        
        return datetime.now()

    def _extract_date_from_meta(self, article):
        try:
            if hasattr(article, 'meta_data') and article.meta_data:
                meta = article.meta_data
                date_tags = [
                    'pubdate', 'publish_date', 'article:published_time', 
                    'date', 'og:published_time', 'publication_date'
                ]
                
                for tag in date_tags:
                    if tag in meta:
                        date_str = meta[tag]
                        parsed_date = self._parse_date_string(date_str)
                        if parsed_date:
                            return parsed_date
        except Exception:
            pass
        return None

    def _extract_date_from_url(self, url: str):
        try:
            patterns = [
                r'/(\d{4})/(\d{2})/(\d{2})/',
                r'/(\d{4})-(\d{2})-(\d{2})/',
                r'/(\d{2})\.(\d{2})\.(\d{4})/',
                r'_(\d{4})(\d{2})(\d{2})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        year, month, day = map(int, groups)
                        return datetime(year, month, day)
        except Exception:
            pass
        return None

    def _parse_date_string(self, date_str: str):
        if not date_str:
            return None
            
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%d.%m.%Y %H:%M',
            '%Y-%m-%d',
            '%d/%m/%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

class TgParser:
    def __init__(self, api_id: int, api_hash: str, phone: str):
        self.client = TelegramClient('session', api_id, api_hash)
        self.phone = phone

    def get_messages(self, channel_username: str, limit: int = 10):
        async def _wrapper():
            await self.client.start(phone=self.phone)
            
            messages_data = []
            async for message in self.client.iter_messages(channel_username, limit=limit):
                if message.text:
                    messages_data.append({
                        'header': message.text[:100] + '...' if len(message.text) > 100 else message.text,
                        'text': message.text,
                        'date': message.date,
                        'url': f"https://t.me/{channel_username.replace('@', '')}/{message.id}"
                    })
            
            await self.client.disconnect()
            return messages_data

        return asyncio.run(_wrapper())