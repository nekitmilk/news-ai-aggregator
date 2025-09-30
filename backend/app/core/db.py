from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Source, Category, ProcessedNews

from datetime import datetime, timedelta
import uuid

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
    
    init_news_data(session)

def init_news_data(session: Session) -> None:
    """
    Initialize news sources, categories and sample news
    """
    # Источники новостей
    sources_data = [
        {"name": "ТАСС", "domain": "tass.ru"},
        {"name": "РБК", "domain": "rbc.ru"},
        {"name": "РИА Новости", "domain": "ria.ru"},
        {"name": "Интерфакс", "domain": "interfax.ru"},
        {"name": "Коммерсант", "domain": "kommersant.ru"},
    ]
    
    sources = {}
    for source_data in sources_data:
        existing_source = session.exec(
            select(Source).where(Source.name == source_data["name"])
        ).first()
        if not existing_source:
            source = Source(**source_data)
            session.add(source)
            session.flush()
            sources[source_data["name"]] = source
        else:
            sources[source_data["name"]] = existing_source

    # Категории новостей
    categories_data = [
        {"name": "Политика"},
        {"name": "Экономика"},
        {"name": "Спорт"},
        {"name": "Технологии"},
        {"name": "Общество"},
        {"name": "Культура"},
        {"name": "Наука"},
        {"name": "Медицина"},
    ]
    
    categories = {}
    for category_data in categories_data:
        existing_category = session.exec(
            select(Category).where(Category.name == category_data["name"])
        ).first()
        if not existing_category:
            category = Category(**category_data)
            session.add(category)
            session.flush()
            categories[category_data["name"]] = category
        else:
            categories[category_data["name"]] = existing_category

    session.commit()

    # Тестовые новости (используем правильное имя модели ProcessedNews)
    sample_news = [
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

    # Добавляем новости, если их еще нет (используем ProcessedNews)
    for news_data in sample_news:
        existing_news = session.exec(
            select(ProcessedNews).where(ProcessedNews.title == news_data["title"])  # ← ProcessedNews!
        ).first()
        
        if not existing_news:
            news = ProcessedNews(  # ← ProcessedNews!
                id=uuid.uuid4(),
                title=news_data["title"],
                summary=news_data["summary"],
                url=news_data["url"],
                published_at=news_data["published_at"],
                source_id=sources[news_data["source"]].id,
                category_id=categories[news_data["category"]].id
            )
            session.add(news)

    session.commit()