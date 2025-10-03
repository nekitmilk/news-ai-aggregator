from .news import router as news_router
from .sources import router as sources_router
from .categories import router as categories_router

# Все роутеры будут автоматически импортированы
__all__ = ["news_router", "sources_router", "categories_router"]