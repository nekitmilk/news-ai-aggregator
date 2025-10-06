from fastapi import APIRouter

from app.api.routes import (
    utils,
    news,
    categories,
    sources,
    user_filters,
    recommendations,
    user_history,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(utils.router)
api_router.include_router(news.router)
api_router.include_router(categories.router)
api_router.include_router(sources.router)
api_router.include_router(user_filters.router)
api_router.include_router(recommendations.router)
api_router.include_router(user_history.router)

