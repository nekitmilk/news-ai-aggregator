from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.api.deps import SessionDep
from app import crud
from app.models import NewsResponse, NewsFilter, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response
import uuid
from dateutil import parser
from dateutil.tz import tzutc

router = APIRouter(prefix="/news", tags=["news"])

@router.get(
    "",
    responses={
        200: {"model": ResponseAPI, "description": "News retrieved successfully"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def get_news(
    session: SessionDep,
    category: Optional[List[uuid.UUID]] = Query(None, alias="category[]", description="Array of category UUIDs"),
    source: Optional[List[uuid.UUID]] = Query(None, alias="source[]", description="Array of source UUIDs"),
    search: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None), 
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("desc", regex="^(asc|desc)$"),
):
    """
    Get news with filters
    """
    try:
        # Конвертируем даты
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = parser.parse(start_date, dayfirst=True)
                if start_dt.tzinfo is not None:
                    start_dt = start_dt.replace(tzinfo=None)

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid start_date format: {str(e)}"
                )
        
        if end_date:
            try:
                end_dt = parser.parse(end_date, dayfirst=True)
                if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                if end_dt.tzinfo is not None:
                    end_dt = end_dt.replace(tzinfo=None)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid end_date format: {str(e)}"
                )
        
        filters = NewsFilter(
            category_ids=category,  # Уже список UUID
            source_ids=source,      # Уже список UUID
            search=search,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            limit=limit,
            sort_order=sort
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
                date=item.published_at.strftime("%d.%m.%Y") if item.published_at else ""
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