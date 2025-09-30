from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, news, categories, sources
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(news.router)
api_router.include_router(categories.router)
api_router.include_router(sources.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
