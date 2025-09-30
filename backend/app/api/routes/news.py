from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.api.deps import SessionDep
from app import crud
from app.models import NewsResponse, NewsFilter, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response

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
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None), 
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get news with filters
    """
    try:
        # Convert string dates to datetime if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)"
                )
        
        filters = NewsFilter(
            category=category,
            source=source, 
            search=search,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            limit=limit
        )
        
        news_items = crud.get_news_with_filters(session, filters)
        
        # Convert to response format
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
        # Re-raise already handled HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving news: {str(e)}"
        )