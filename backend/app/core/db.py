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
    base_news = [
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
    
    # Дополнительные новости для достижения 100
    additional_news = [
        # Политика
        {
            "title": "Президент провел встречу с главами регионов",
            "summary": "Обсуждались вопросы социально-экономического развития субъектов федерации.",
            "url": "https://example.com/news/11",
            "published_at": datetime.now() - timedelta(hours=1),
            "source": "ТАСС",
            "category": "Политика"
        },
        {
            "title": "Парламент рассмотрит новый законопроект",
            "summary": "Депутаты готовятся к обсуждению важного законодательного акта.",
            "url": "https://example.com/news/12",
            "published_at": datetime.now() - timedelta(hours=4),
            "source": "РИА Новости",
            "category": "Политика"
        },
        {
            "title": "Международные переговоры завершились успехом",
            "summary": "Стороны достигли договоренностей по ключевым вопросам сотрудничества.",
            "url": "https://example.com/news/13",
            "published_at": datetime.now() - timedelta(days=1),
            "source": "Интерфакс",
            "category": "Политика"
        },
        {
            "title": "Реформа государственного управления",
            "summary": "Планируется оптимизация структуры федеральных органов власти.",
            "url": "https://example.com/news/14",
            "published_at": datetime.now() - timedelta(days=2),
            "source": "РБК",
            "category": "Политика"
        },
        {
            "title": "Визит иностранной делегации в Москву",
            "summary": "Официальная делегация прибыла для проведения двусторонних консультаций.",
            "url": "https://example.com/news/15",
            "published_at": datetime.now() - timedelta(hours=6),
            "source": "Коммерсант",
            "category": "Политика"
        },

        # Экономика
        {
            "title": "Рубль укрепился к основным валютам",
            "summary": "Курс национальной валюты показал положительную динамику на биржевых торгах.",
            "url": "https://example.com/news/16",
            "published_at": datetime.now() - timedelta(hours=3),
            "source": "ТАСС",
            "category": "Экономика"
        },
        {
            "title": "Инфляция замедлилась до 5,8%",
            "summary": "Потребительские цены демонстрируют умеренный рост в годовом выражении.",
            "url": "https://example.com/news/17",
            "published_at": datetime.now() - timedelta(days=1),
            "source": "РИА Новости",
            "category": "Экономика"
        },
        {
            "title": "Инвестиции в промышленность выросли на 12%",
            "summary": "Объем капиталовложений в обрабатывающие производства показал значительный рост.",
            "url": "https://example.com/news/18",
            "published_at": datetime.now() - timedelta(days=3),
            "source": "Интерфакс",
            "category": "Экономика"
        },
        {
            "title": "Фондовый рынок обновил исторический максимум",
            "summary": "Индексы Московской биржи достигли рекордных значений.",
            "url": "https://example.com/news/19",
            "published_at": datetime.now() - timedelta(hours=7),
            "source": "РБК",
            "category": "Экономика"
        },
        {
            "title": "Экспорт сельхозпродукции увеличился на 15%",
            "summary": "Поставки российской аграрной продукции на внешние рынки продолжают расти.",
            "url": "https://example.com/news/20",
            "published_at": datetime.now() - timedelta(days=2),
            "source": "Коммерсант",
            "category": "Экономика"
        },

        # Спорт
        {
            "title": "Футбольный клуб одержал победу в дерби",
            "summary": "В принципиальном матче местная команда обыграла своего давнего соперника.",
            "url": "https://example.com/news/21",
            "published_at": datetime.now() - timedelta(hours=2),
            "source": "ТАСС",
            "category": "Спорт"
        },
        {
            "title": "Хоккеисты вышли в плей-офф чемпионата",
            "summary": "Комда успешно завершила регулярный сезон и продолжит борьбу за титул.",
            "url": "https://example.com/news/22",
            "published_at": datetime.now() - timedelta(days=1),
            "source": "РИА Новости",
            "category": "Спорт"
        },
        {
            "title": "Олимпийский комитет утвердил состав сборной",
            "summary": "Определен список спортсменов, которые представят страну на международных соревнованиях.",
            "url": "https://example.com/news/23",
            "published_at": datetime.now() - timedelta(days=4),
            "source": "Интерфакс",
            "category": "Спорт"
        },
        {
            "title": "Теннисистка вышла в финал турнира",
            "summary": "Российская спортсменка уверенно прошла полуфинальную стадию соревнований.",
            "url": "https://example.com/news/24",
            "published_at": datetime.now() - timedelta(hours=5),
            "source": "РБК",
            "category": "Спорт"
        },
        {
            "title": "Строительство нового стадиона nearing completion",
            "summary": "Работы на спортивном объекте выходят на финишную прямую.",
            "url": "https://example.com/news/25",
            "published_at": datetime.now() - timedelta(days=3),
            "source": "Коммерсант",
            "category": "Спорт"
        },

        # Технологии
        {
            "title": "Запуск нового мобильного приложения",
            "summary": "Разработчики представили инновационное решение для удаленного доступа к услугам.",
            "url": "https://example.com/news/26",
            "published_at": datetime.now() - timedelta(hours=1),
            "source": "ТАСС",
            "category": "Технологии"
        },
        {
            "title": "Искусственный интеллект поможет медикам",
            "summary": "Нейросеть научилась диагностировать заболевания с высокой точностью.",
            "url": "https://example.com/news/27",
            "published_at": datetime.now() - timedelta(days=2),
            "source": "РИА Новости",
            "category": "Технологии"
        },
        {
            "title": "Кибербезопасность: новые вызовы",
            "summary": "Эксперты обсудили актуальные угрозы в цифровом пространстве.",
            "url": "https://example.com/news/28",
            "published_at": datetime.now() - timedelta(hours=8),
            "source": "Интерфакс",
            "category": "Технологии"
        },
        {
            "title": "5G сети развернут в крупных городах",
            "summary": "Операторы связи приступают к массовому внедрению технологии пятого поколения.",
            "url": "https://example.com/news/29",
            "published_at": datetime.now() - timedelta(days=5),
            "source": "РБК",
            "category": "Технологии"
        },
        {
            "title": "Роботизация производственных процессов",
            "summary": "Предприятия активно внедряют автоматизированные системы управления.",
            "url": "https://example.com/news/30",
            "published_at": datetime.now() - timedelta(days=4),
            "source": "Коммерсант",
            "category": "Технологии"
        },

        # Общество
        {
            "title": "Социологический опрос: доверие к институтам выросло",
            "summary": "Исследование показало повышение уровня общественного доверия к государственным структурам.",
            "url": "https://example.com/news/31",
            "published_at": datetime.now() - timedelta(days=1),
            "source": "ТАСС",
            "category": "Общество"
        },
        {
            "title": "Волонтерское движение набирает популярность",
            "summary": "Количество участников добровольческих организаций увеличилось на 25%.",
            "url": "https://example.com/news/32",
            "published_at": datetime.now() - timedelta(days=3),
            "source": "РИА Новости",
            "category": "Общество"
        },
        {
            "title": "Образовательные программы для старшего поколения",
            "summary": "Пенсионеры активно осваивают цифровые технологии на специальных курсах.",
            "url": "https://example.com/news/33",
            "published_at": datetime.now() - timedelta(hours=6),
            "source": "Интерфакс",
            "category": "Общество"
        },
        {
            "title": "Благоустройство городских территорий",
            "summary": "В рамках федеральной программы создаются новые общественные пространства.",
            "url": "https://example.com/news/34",
            "published_at": datetime.now() - timedelta(days=2),
            "source": "РБК",
            "category": "Общество"
        },
        {
            "title": "Поддержка многодетных семей расширена",
            "summary": "Правительство утвердило дополнительные меры социальной помощи.",
            "url": "https://example.com/news/35",
            "published_at": datetime.now() - timedelta(days=4),
            "source": "Коммерсант",
            "category": "Общество"
        },

        # Культура
        {
            "title": "Театральный фестиваль откроется на следующей неделе",
            "summary": "Зрителей ждут премьеры спектаклей от ведущих режиссеров страны.",
            "url": "https://example.com/news/36",
            "published_at": datetime.now() - timedelta(hours=3),
            "source": "ТАСС",
            "category": "Культура"
        },
        {
            "title": "Кинопремия: объявлены номинанты",
            "summary": "Оглашен список фильмов, претендующих на главные награды года.",
            "url": "https://example.com/news/37",
            "published_at": datetime.now() - timedelta(days=1),
            "source": "РИА Новости",
            "category": "Культура"
        },
        {
            "title": "Выставка редких книг в национальной библиотеке",
            "summary": "Посетители смогут увидеть уникальные издания из фондов хранилища.",
            "url": "https://example.com/news/38",
            "published_at": datetime.now() - timedelta(days=5),
            "source": "Интерфакс",
            "category": "Культура"
        },
        {
            "title": "Музыкальный коллектив готовит новый альбом",
            "summary": "Известная группа анонсировала выход студийной работы после трехлетнего перерыва.",
            "url": "https://example.com/news/39",
            "published_at": datetime.now() - timedelta(hours=9),
            "source": "РБК",
            "category": "Культура"
        },
        {
            "title": "Реставрация памятника архитектуры завершена",
            "summary": "Историческое здание восстановлено в первоначальном виде.",
            "url": "https://example.com/news/40",
            "published_at": datetime.now() - timedelta(days=6),
            "source": "Коммерсант",
            "category": "Культура"
        },

        # Наука
        {
            "title": "Археологи обнаружили древнее поселение",
            "summary": "Уникальная находка прольет свет на историю региона.",
            "url": "https://example.com/news/41",
            "published_at": datetime.now() - timedelta(days=2),
            "source": "ТАСС",
            "category": "Наука"
        },
        {
            "title": "Физики приблизились к созданию квантового компьютера",
            "summary": "Ученые добились прорыва в области квантовых вычислений.",
            "url": "https://example.com/news/42",
            "published_at": datetime.now() - timedelta(days=4),
            "source": "РИА Новости",
            "category": "Наука"
        },
        {
            "title": "Экспедиция в Арктику собрала уникальные данные",
            "summary": "Исследователи изучили изменения климата в северных широтах.",
            "url": "https://example.com/news/43",
            "published_at": datetime.now() - timedelta(days=7),
            "source": "Интерфакс",
            "category": "Наука"
        },
        {
            "title": "Биологи открыли новый вид растений",
            "summary": "Научное сообщество пополнилось важным ботаническим открытием.",
            "url": "https://example.com/news/44",
            "published_at": datetime.now() - timedelta(days=3),
            "source": "РБК",
            "category": "Наука"
        },
        {
            "title": "Астрономы наблюдали редкое космическое явление",
            "summary": "Ученые зафиксировали уникальное расположение планет в солнечной системе.",
            "url": "https://example.com/news/45",
            "published_at": datetime.now() - timedelta(hours=10),
            "source": "Коммерсант",
            "category": "Наука"
        },

        # Медицина
        {
            "title": "Новая поликлиника открылась в жилом районе",
            "summary": "Медицинское учреждение оснащено современным диагностическим оборудованием.",
            "url": "https://example.com/news/46",
            "published_at": datetime.now() - timedelta(days=1),
            "source": "ТАСС",
            "category": "Медицина"
        },
        {
            "title": "Вакцина от гриппа: обновленный штамм",
            "summary": "Фармацевтические компании начали производство сезонной вакцины.",
            "url": "https://example.com/news/47",
            "published_at": datetime.now() - timedelta(days=5),
            "source": "РИА Новости",
            "category": "Медицина"
        },
        {
            "title": "Телемедицина: удобство и доступность",
            "summary": "Удаленные консультации врачей становятся все более популярными.",
            "url": "https://example.com/news/48",
            "published_at": datetime.now() - timedelta(hours=7),
            "source": "Интерфакс",
            "category": "Медицина"
        },
        {
            "title": "Медицинский туризм: рост потока пациентов",
            "summary": "Иностранные граждане активно выбирают российские клиники для лечения.",
            "url": "https://example.com/news/49",
            "published_at": datetime.now() - timedelta(days=4),
            "source": "РБК",
            "category": "Медицина"
        },
        {
            "title": "Инновации в кардиохирургии",
            "summary": "Врачи освоили новую методику операций на сердце.",
            "url": "https://example.com/news/50",
            "published_at": datetime.now() - timedelta(days=6),
            "source": "Коммерсант",
            "category": "Медицина"
        }
    ]
    
    # Генерация еще 50 новостей для достижения 100
    extra_news = []
    for i in range(51, 101):
        category = random.choice(CATEGORIES_DATA)["name"]
        source = random.choice(SOURCE_DATA)["name"]
        
        news_templates = [
            {
                "title": f"Новое исследование в области {category}",
                "summary": f"Ученые представили результаты масштабного исследования по актуальной теме.",
                "url": f"https://example.com/news/{i}",
                "published_at": datetime.now() - timedelta(hours=random.randint(1, 168)),
                "source": source,
                "category": category
            },
            {
                "title": f"Развитие {category} в регионах",
                "summary": f"Региональные власти представили план развития отрасли на ближайшие годы.",
                "url": f"https://example.com/news/{i+50}",
                "published_at": datetime.now() - timedelta(hours=random.randint(1, 168)),
                "source": source,
                "category": category
            },
            {
                "title": f"Эксперты обсуждают будущее {category}",
                "summary": f"Ведущие специалисты собрались для обсуждения перспектив развития направления.",
                "url": f"https://example.com/news/{i+100}",
                "published_at": datetime.now() - timedelta(hours=random.randint(1, 168)),
                "source": source,
                "category": category
            }
        ]
        
        template = random.choice(news_templates)
        extra_news.append(template)
    
    return base_news + additional_news + extra_news


# ---------- Основные функции ----------
def init_db(session: Session) -> None:
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

    crud.create_vectors_for_unprocessed_news(session)


if __name__ == "__main__":
    with Session(engine) as session:
        init_db(session)