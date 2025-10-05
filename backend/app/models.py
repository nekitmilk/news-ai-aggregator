import uuid
from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, field_validator, ConfigDict
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Text, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import UUID as SA_UUID


# ===== BASE RESPONSE MODELS =====
class ErrorResponse(SQLModel):
    code: int
    message: str

class HTTPErrorResponse(BaseModel):
    detail: str

class ResponseAPI(SQLModel):
    success: bool
    requestId: str
    message: str
    result: Optional[Any] = None
    errors: Optional[ErrorResponse] = None

    class Config:
        from_attributes = True

# ===== Source MODELS =====
class Source(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=255)
    domain: str = Field(max_length=255)
    news: list["ProcessedNews"] = Relationship(back_populates="source")

class SourceBase(SQLModel):
    name: str
    domain: str

class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: uuid.UUID

class SourceListResponse(ResponseAPI):
    result: List[SourceResponse]


# ===== Category MODELS =====
class Category(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    news: list["ProcessedNews"] = Relationship(back_populates="category")

class CategoryBase(SQLModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: uuid.UUID

class CategoriesListResponse(ResponseAPI):
    result: List[CategoryResponse]


# ===== NEWS MODELS =====
class ProcessedNews(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(index=True, max_length=500)
    summary: str = Field(sa_type=Text)
    url: str = Field(max_length=500)
    published_at: datetime = Field(index=True)
    
    # Внешние ключи
    source_id: uuid.UUID = Field(foreign_key="source.id")
    category_id: uuid.UUID = Field(foreign_key="category.id")
    
    # Связи
    source: Source = Relationship(back_populates="news")
    category: Category = Relationship(back_populates="news")

class NewsBase(SQLModel):
    title: str
    summary: str
    url: str
    published_at: datetime

class NewsCreate(NewsBase):
    source_id: uuid.UUID
    category_id: uuid.UUID

class NewsResponse(SQLModel):
    id: uuid.UUID
    title: str
    summary: str  
    category: str 
    source: str
    url: str
    date: str  # Дата публикации в формате "dd.mm.YYYY"

class NewsListResponse(ResponseAPI):
    result: List[NewsResponse]

class NewsFilter(BaseModel):
    category_ids: Optional[List[uuid.UUID]] = None
    source_ids: Optional[List[uuid.UUID]] = None
    search: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    limit: int = 20
    sort_order: str = "desc"

# ===== USER FILTER MODELS =====
class UserFilter(SQLModel, table=True):
    user_id: int = Field(primary_key=True)  # Telegram ID как первичный ключ
    category: List[uuid.UUID] = Field(default=[], sa_column=Column(ARRAY(SA_UUID)))
    source: List[uuid.UUID] = Field(default=[], sa_column=Column(ARRAY(SA_UUID)))
    search: Optional[str] = Field(default=None, max_length=500)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    sort: Optional[str] = Field(default=None, max_length=10)  # "asc" or "desc"
    # по хорошему установить связь с таблицей user_history

class UserFilterBase(SQLModel):
    category: Optional[List[uuid.UUID]] = None
    source: Optional[List[uuid.UUID]] = None
    search: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort: Optional[str] = None

    model_config = ConfigDict(validate_assignment=True)

    @field_validator('sort')
    @classmethod
    def validate_sort_order(cls, v):
        if v is not None:
            v_lower = v.lower()
            if v_lower not in ['asc', 'desc']:
                raise ValueError('Sort must be either "asc" or "desc"')
            return v_lower
        return v

class UserFilterCreate(UserFilterBase):
    pass

class UserFilterUpdate(UserFilterBase):
    pass

class UserFilterResponse(UserFilterBase):
    user_id: int

class UserFilterListResponse(ResponseAPI):
    result: List[UserFilterResponse]

class UserFilterSingleResponse(ResponseAPI):
    result: UserFilterResponse

class UserFilterIdResponse(ResponseAPI):
    result: dict  # {"user_id": 12345}