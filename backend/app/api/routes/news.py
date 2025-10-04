from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.api.deps import SessionDep
from app import crud
from app.models import NewsResponse, NewsFilter, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response
import uuid

router = APIRouter(prefix="/news", tags=["news"])

@router.get(
    "/",
    responses={
        200: {"model": ResponseAPI, "description": "News retrieved successfully"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def get_news(
    session: SessionDep,
    category_ids: Optional[str] = Query(None, description="Comma-separated category UUIDs"),
    source_ids: Optional[str] = Query(None, description="Comma-separated source UUIDs"),
    search: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None), 
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """
    Get news with filters
    """
    try:
        # Парсим массивы ID из строк
        parsed_category_ids = None
        parsed_source_ids = None
        
        if category_ids:
            try:
                parsed_category_ids = [uuid.UUID(cid.strip()) for cid in category_ids.split(",")]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid category IDs format. Use comma-separated UUIDs"
                )
        
        if source_ids:
            try:
                parsed_source_ids = [uuid.UUID(sid.strip()) for sid in source_ids.split(",")]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid source IDs format. Use comma-separated UUIDs"
                )
        
        # Конвертируем даты
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"
                )
        
        filters = NewsFilter(
            category_ids=parsed_category_ids,
            source_ids=parsed_source_ids, 
            search=search,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            limit=limit,
            sort_order=sort_order
        )
        
        news_items = crud.get_news_with_filters(session, filters)
        
        # Конвертируем в формат ответа
        result = []
        for item in news_items:
            result.append(NewsResponse(
                id=item.id,
                title=item.title,
                summary=item.summary,
                category=item.category.name,
                source=item.source.name,
                url=item.url,
                date=item.published_at.strftime("%d:%m:%Y") if item.published_at else ""
            ))
        
        return create_success_response(
            result=result,
            message="News retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving news: {str(e)}"
        )