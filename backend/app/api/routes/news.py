import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, HTTPException, status

from app.api.deps import SessionDep
from app import crud
from app.models import NewsResponse, NewsFilter, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])


def _parse_date(date_str: Optional[str], field_name: str) -> Optional[datetime]:
    """Parse ISO date string to datetime or raise HTTPException."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        logger.warning(f"Invalid date format for {field_name}: {date_str}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {field_name} format. Use ISO format (YYYY-MM-DD)"
        )


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
    Get news with optional filters: category, source, search, date range, pagination.
    """
    logger.info(f"Fetching news: category={category}, source={source}, search={search}, "
                f"start_date={start_date}, end_date={end_date}, page={page}, limit={limit}")

    try:
        # Parse dates
        start_dt = _parse_date(start_date, "start_date")
        end_dt = _parse_date(end_date, "end_date")

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

        result = [
            NewsResponse(
                id=item.id,
                title=item.title,
                summary=item.summary,
                category=item.category.name if item.category else None,
                source=item.source.name if item.source else None,
                url=item.url,
                date=item.published_at.strftime("%d:%m:%Y") if item.published_at else ""
            )
            for item in news_items
        ]

        logger.info(f"Retrieved {len(result)} news items")
        return create_success_response(result=result, message="News retrieved successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error while retrieving news")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving news: {str(e)}"
        )
