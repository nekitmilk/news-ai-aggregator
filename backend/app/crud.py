import uuid
from typing import Any, List
from sqlmodel import Session, select
from app.models import (
    Source, 
    Category, 
    ProcessedNews, 
    NewsFilter, 
    SourceCreate, 
    CategoryCreate,
    UserFilter,
    UserFilterCreate,
    UserFilterUpdate
)


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

    conditions = []
    
    if filters.category_ids:
        conditions.append(Category.id.in_(filters.category_ids))
    if filters.source_ids:
        conditions.append(Source.id.in_(filters.source_ids))
    if filters.search:
        search_term = f"%{filters.search}%"
        conditions.append(
            (ProcessedNews.title.ilike(search_term)) | 
            (ProcessedNews.summary.ilike(search_term))
        )
    if filters.start_date:
        conditions.append(ProcessedNews.published_at >= filters.start_date)
    if filters.end_date:
        conditions.append(ProcessedNews.published_at <= filters.end_date)
    
    if conditions:
        statement = statement.where(*conditions)
    
    if filters.sort_order == "asc":
        statement = statement.order_by(ProcessedNews.published_at.asc())
    else:
        statement = statement.order_by(ProcessedNews.published_at.desc())
    
    skip = (filters.page - 1) * filters.limit
    statement = statement.offset(skip).limit(filters.limit)
    
    return session.exec(statement).all()

# UserFilter CRUD operations
def create_user_filter(*, session: Session, user_id: int, filter_create: UserFilterCreate) -> UserFilter:
    db_obj = UserFilter(**filter_create.model_dump(), user_id=user_id)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_user_filter(*, session: Session, user_id: int) -> UserFilter | None:
    return session.get(UserFilter, user_id)

def get_all_user_filters(session: Session, page: int = 1, limit: int = 100) -> List[UserFilter]:
    skip = (page - 1) * limit
    statement = select(UserFilter).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_user_filter(*, session: Session, user_id: int, filter_update: UserFilterUpdate) -> UserFilter | None:
    db_filter = session.get(UserFilter, user_id)
    if not db_filter:
        return None
    
    update_data = filter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_filter, field, value)
    
    session.add(db_filter)
    session.commit()
    session.refresh(db_filter)
    return db_filter

def delete_user_filter(*, session: Session, user_id: int) -> bool:
    user_filter = session.get(UserFilter, user_id)
    if not user_filter:
        return False
    session.delete(user_filter)
    session.commit()
    return True