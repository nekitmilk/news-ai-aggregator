import uuid
from datetime import datetime
from typing import Optional, List, Any

from pydantic import EmailStr
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Text


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


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
    date: str  # Дата публикации в формате "dd:mm:YYYY"

class NewsListResponse(ResponseAPI):
    result: List[NewsResponse]

class NewsFilter(BaseModel):
    category: Optional[str] = None
    source: Optional[str] = None
    search: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    limit: int = 20
