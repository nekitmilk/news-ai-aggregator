import uuid
from typing import Any, List
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate, Source, Category, ProcessedNews, NewsFilter, SourceCreate, CategoryCreate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def create_source(*, session: Session, source_create: SourceCreate) -> Source:
    db_obj = Source.model_validate(source_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_source(*, session: Session, source_id: uuid.UUID) -> bool:
    source = session.get(Source, source_id)
    if not source:
        return False
    session.delete(source)
    session.commit()
    return True

def get_source_by_id(*, session: Session, source_id: uuid.UUID) -> Source | None:
    return session.get(Source, source_id)

def get_sources(session: Session, page: int = 0, limit: int = 100) -> List[Source]:
    skip = (page - 1) * limit
    statement = select(Source).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_category(*, session: Session, category_create: CategoryCreate) -> Category:
    db_obj = Category.model_validate(category_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_category(*, session: Session, category_id: uuid.UUID) -> bool:
    category = session.get(Category, category_id)
    if not category:
        return False
    session.delete(category)
    session.commit()
    return True

def get_category_by_id(*, session: Session, category_id: uuid.UUID) -> Category | None:
    return session.get(Category, category_id)

def get_categories(session: Session, page: int = 0, limit: int = 100) -> List[Category]:
    skip = (page - 1) * limit
    statement = select(Category).offset(skip).limit(limit)
    return session.exec(statement).all()

def get_news_with_filters(session: Session, filters: NewsFilter) -> List[ProcessedNews]:
    statement = select(ProcessedNews).join(Source).join(Category)
    
    if filters.category:
        statement = statement.where(Category.name == filters.category)
    if filters.source:
        statement = statement.where(Source.name == filters.source)
    if filters.search:
        search_term = f"%{filters.search}%"
        statement = statement.where(
            (ProcessedNews.title.ilike(search_term)) | 
            (ProcessedNews.summary.ilike(search_term))
        )
    if filters.start_date:
        statement = statement.where(ProcessedNews.published_at >= filters.start_date)
    if filters.end_date:
        statement = statement.where(ProcessedNews.published_at <= filters.end_date)
    
    statement = statement.order_by(ProcessedNews.published_at.desc())
    skip = (filters.page - 1) * filters.limit
    statement = statement.offset(skip).limit(filters.limit)
    
    return session.exec(statement).all()