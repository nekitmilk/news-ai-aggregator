from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Source, Category, ProcessedNews

from datetime import datetime, timedelta
import uuid

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
    return [
        {
            "title": "ЦБ сохранил ключевую ставку на уровне 16%",
            "summary": "Центральный банк России принял решение сохранить ключевую ставку на уровне 16% годовых.",
            "url": "https://example.com/news/1",
            "published_at": datetime.now() - timedelta(hours=2),
            "source": "ТАСС",
            "category": "Экономика"
        },
        {
            "title": "Новые санкции против российских компаний",
            "summary": "Евросоюз ввел новые ограничительные меры против ряда российских компаний.",
            "url": "https://example.com/news/2",
            "published_at": datetime.now() - timedelta(days=1),
            "source": "РИА Новости",
            "category": "Политика"
        },
        {
            "title": "Российские спортсмены завоевали 5 золотых медалей",
            "summary": "На международных соревнованиях российские атлеты показали выдающиеся результаты.",
            "url": "https://example.com/news/3",
            "published_at": datetime.now() - timedelta(days=2),
            "source": "РБК",
            "category": "Спорт"
        },
        {
            "title": "Ученые разработали новый метод лечения рака",
            "summary": "Российские исследователи представили инновационный подход к терапии онкологических заболеваний.",
            "url": "https://example.com/news/4",
            "published_at": datetime.now() - timedelta(days=3),
            "source": "Интерфакс",
            "category": "Медицина"
        },
        {
            "title": "Выставка современного искусства открывается в Москве",
            "summary": "В столице стартует масштабная выставка работ современных российских художников.",
            "url": "https://example.com/news/5",
            "published_at": datetime.now() - timedelta(hours=5),
            "source": "Коммерсант",
            "category": "Культура"
        },
        {
            "title": "Запуск новой космической программы",
            "summary": "Роскосмос анонсировал начало реализации новой лунной программы.",
            "url": "https://example.com/news/6",
            "published_at": datetime.now() - timedelta(days=1, hours=3),
            "source": "ТАСС",
            "category": "Наука"
        },
        {
            "title": "Цифровизация госуслуг ускорится",
            "summary": "Правительство утвердило план по ускорению цифровой трансформации государственных услуг.",
            "url": "https://example.com/news/7",
            "published_at": datetime.now() - timedelta(hours=8),
            "source": "РИА Новости",
            "category": "Технологии"
        },
        {
            "title": "Изменения в пенсионной системе",
            "summary": "Внесены поправки в законодательство о пенсионном обеспечении граждан.",
            "url": "https://example.com/news/8",
            "published_at": datetime.now() - timedelta(days=4),
            "source": "РБК",
            "category": "Общество"
        },
        {
            "title": "Новые меры поддержки малого бизнеса",
            "summary": "Правительство расширило программу льготного кредитования для предпринимателей.",
            "url": "https://example.com/news/9",
            "published_at": datetime.now() - timedelta(days=2, hours=6),
            "source": "Интерфакс",
            "category": "Экономика"
        },
        {
            "title": "Фестиваль уличного искусства пройдет в Санкт-Петербурге",
            "summary": "В северной столице состоится ежегодный фестиваль граффити и уличных перформансов.",
            "url": "https://example.com/news/10",
            "published_at": datetime.now() - timedelta(days=1, hours=12),
            "source": "Коммерсант",
            "category": "Культура"
        }
    ]


# ---------- Основные функции ----------
def init_db(session: Session) -> None:
    """
    Инициализация базы: создание суперпользователя и базовых данных
    """
    # создаём суперпользователя, если его ещё нет
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        crud.create_user(session=session, user_create=user_in)

    init_news_data(session)


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

    session.commit()
