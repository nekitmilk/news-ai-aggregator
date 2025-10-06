from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import Source, Category, ProcessedNews
# from app.models import User, UserCreate, Source, Category, ProcessedNews

from datetime import datetime, timedelta
import uuid
import random

# ---------- Инициализация движка ----------
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# ---------- Константы ----------
CATEGORIES_DATA = [
    {"name": "Политика"},
    {"name": "Экономика"},
    {"name": "Спорт"},
    {"name": "Технологии"},
    {"name": "Общество"},
    {"name": "Культура"},
    {"name": "Наука"},
    {"name": "Медицина"},
]

SOURCE_DATA = [
    {"name": "ТАСС", "domain": "tass.ru"},
    {"name": "РБК", "domain": "rbc.ru"},
    {"name": "РИА Новости", "domain": "ria.ru"},
    {"name": "Интерфакс", "domain": "interfax.ru"},
    {"name": "Коммерсант", "domain": "kommersant.ru"},
]


# ---------- Вспомогательные функции ----------
def get_or_create(session: Session, model, filters: dict, defaults: dict = None):
    """Ищет объект по filters, если нет — создаёт с defaults"""
    instance = session.exec(select(model).filter_by(**filters)).first()
    if instance:
        return instance
    data = {**filters, **(defaults or {})}
    instance = model(**data)
    session.add(instance)
    session.flush()  # нужно, чтобы у instance появился id
    return instance


def generate_sample_news():
    """Возвращает список тестовых новостей с динамическими датами"""
    base_news = []
    
    # Дополнительные новости для достижения 100
    additional_news = []
    
    # Генерация еще 50 новостей для достижения 100
    extra_news = []
    for i in range(51, 101):
        category = random.choice(CATEGORIES_DATA)["name"]
        source = random.choice(SOURCE_DATA)["name"]
        
        news_templates = []
        
        template = random.choice(news_templates)
        extra_news.append(template)
    
    return base_news + additional_news + extra_news


# ---------- Основные функции ----------
def init_db(session: Session) -> None:
    # init_news_data(session)
    crud.create_vectors_for_unprocessed_news(session)


def init_news_data(session: Session) -> None:
    """
    Инициализация новостных источников, категорий и тестовых новостей
    """
    # создаём источники
    sources = {
        s["name"]: get_or_create(session, Source, {"name": s["name"]}, {"domain": s["domain"]})
        for s in SOURCE_DATA
    }

    # создаём категории
    categories = {
        c["name"]: get_or_create(session, Category, {"name": c["name"]})
        for c in CATEGORIES_DATA
    }

    session.commit()

    # создаём тестовые новости
    news_count = 0
    for news_data in generate_sample_news():
        existing_news = session.exec(
            select(ProcessedNews).where(ProcessedNews.title == news_data["title"])
        ).first()

        if not existing_news:
            news = ProcessedNews(
                id=uuid.uuid4(),
                title=news_data["title"],
                summary=news_data["summary"],
                url=news_data["url"],
                published_at=news_data["published_at"],
                source_id=sources[news_data["source"]].id,
                category_id=categories[news_data["category"]].id,
            )
            session.add(news)
            news_count += 1

    session.commit()
    print(f"Добавлено {news_count} тестовых новостей")    


if __name__ == "__main__":
    with Session(engine) as session:
        init_db(session)