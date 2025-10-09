import uuid
import numpy as np
from app.recommendation_system.news_recommender import (
    Entity,
    NewsRecommender
)
from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from app.models import (
    Source, SourceCreate,
    Category, CategoryCreate,
    ProcessedNews, NewsFilter,
    UserFilter, UserFilterCreate, UserFilterUpdate,
    UserHistory, UserHistoryCreate,
    NewsVector, NewsVectorCreate
)
from app.core.config import settings


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

def get_recent_news_ids(session: Session, limit: int = 1000) -> List[uuid.UUID]:
    statement = (
        select(ProcessedNews.id)
        .order_by(ProcessedNews.published_at.desc())
        .limit(limit)
    )
    
    return session.exec(statement).all()

def get_news_by_ids(session: Session, news_ids: List[uuid.UUID]) -> List[ProcessedNews]:
    if not news_ids:
        return []
    
    statement = (
        select(
            ProcessedNews.id,
            ProcessedNews.title,
            ProcessedNews.summary,
            ProcessedNews.url,
            ProcessedNews.published_at,
            Category.name.label('category_name'),
            Source.name.label('source_name')
        )
        .join(Category, ProcessedNews.category_id == Category.id)
        .join(Source, ProcessedNews.source_id == Source.id)
        .where(ProcessedNews.id.in_(news_ids))
    )
    
    results = session.exec(statement).all()
    news_dict = {news.id: news for news in results}
    return [news_dict[news_id] for news_id in news_ids if news_id in news_dict]

def get_user_history(
    session: Session,
    page: int = 1,
    limit: int = 100,
    user_id: int = None,
    news_id: uuid.UUID = None
) -> List[UserHistory]:
    """Получить историю просмотров с фильтрацией и пагинацией"""
    query = session.query(UserHistory)
    
    if user_id:
        query = query.filter(UserHistory.user_id == user_id)
    if news_id:
        query = query.filter(UserHistory.news_id == news_id)
        
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

def create_user_history(
    session: Session,
    history_create: UserHistoryCreate
) -> UserHistory:
    """Создать запись в истории просмотров"""
    history = UserHistory(**history_create.dict())
    session.add(history)
    session.commit()
    session.refresh(history)
    return history

def get_news_vector_by_news_id(session: Session, news_id: uuid.UUID) -> Optional[NewsVector]:
    """Получить вектор по ID новости"""
    return session.exec(
        select(NewsVector).where(NewsVector.news_id == news_id)
    ).first()

def create_news_vector(session: Session, vector_data: NewsVectorCreate) -> NewsVector:
    """Создать вектор для новости"""
    existing = get_news_vector_by_news_id(session, vector_data.news_id)
    if existing:
        existing.vector = vector_data.vector
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    
    vector = NewsVector(**vector_data.dict())
    session.add(vector)
    session.commit()
    session.refresh(vector)
    return vector

# -------------------------------
 
def get_news_vectors(session: Session, limit: int, page: int) -> List[Entity]:
    query = (
        select(
            ProcessedNews.id,
            NewsVector.vector,
            ProcessedNews.published_at.label('timestamp'),
        )
        .join(NewsVector, ProcessedNews.id == NewsVector.news_id)
        .order_by(ProcessedNews.published_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    
    results = session.exec(query).all()
    
    return [
        Entity(
            id=row.id,
            vector=row.vector,
            timestamp=row.timestamp,
        )
        for row in results
    ]

def get_user_vectors(session: Session, user_id: int) -> List[Entity]:
    query = (
        select(
            UserHistory.news_id,
            NewsVector.vector,
            UserHistory.view_timestamp,
        )
        .join(NewsVector, NewsVector.news_id == UserHistory.news_id)
        .where(UserHistory.user_id == user_id)
        .where(UserHistory.view_timestamp.is_not(None))
        .order_by(UserHistory.view_timestamp.desc())
    )
  
    results = session.exec(query).all()

    return [
        Entity(
            id=row.news_id,
            vector=np.array(row.vector),
            timestamp=row.view_timestamp,
        )
        for row in results
    ]

def get_recommendeted_news(session: Session, user_id: int, limit: int, page: int) -> List[ProcessedNews]:
    recommender = NewsRecommender(
        vector_size=settings.VECTOR_SIZE,
        freshness_weight=settings.FRESHNESS_WEIGHT,
        decay_factor=settings.DECAY_FACTOR,
    )
    
    user_vectors = get_user_vectors(session, user_id)
    coef = settings.LIMIT_COEF if any(user_vectors) else 1
    news_vectors = get_news_vectors(session, coef * limit, page)

    result = recommender.get_recommendations(news_vectors, user_vectors, n=limit)

    return get_news_by_ids(session, result)

def create_vectors_for_unprocessed_news(
    session: Session, 
    batch_size: int = 1000
) -> int:
    unprocessed_news_query = (
        select(ProcessedNews, Category, Source)
        .join(Category, ProcessedNews.category_id == Category.id)
        .join(Source, ProcessedNews.source_id == Source.id)
        .join(NewsVector, ProcessedNews.id == NewsVector.news_id, isouter=True)
        .where(NewsVector.news_id.is_(None))
        .limit(batch_size)
    )
    
    results = session.exec(unprocessed_news_query).all()
    
    created_count = 0
    news_recommender = NewsRecommender(
        vector_size=settings.VECTOR_SIZE,
        freshness_weight=settings.FRESHNESS_WEIGHT,
        decay_factor=settings.DECAY_FACTOR,
    )
    for news, category, source in results:
        try:
            vector = news_recommender.create_news_vector(
                news_id=news.id,
                title=news.title,
                summary=news.summary,
                category=category.name,
                news_timestamp=news.published_at
            )
            
            news_vector_data = NewsVectorCreate(
                news_id=news.id,
                vector=vector.vector,
            )
            
            create_news_vector(session, news_vector_data)
            created_count += 1
            
        except Exception as e:
            print(f"Ошибка при создании вектора для новости {news.id}: {e}")
            session.rollback()
            continue
    
    if created_count > 0:
        session.commit()
    
    return created_count