from fastapi import APIRouter, Query, HTTPException, status
import logging

from app.api.deps import SessionDep
from app import crud
from app.models import NewsResponse, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
logger = logging.getLogger(__name__)

@router.get(
    "/",
    responses={
        200: {"model": ResponseAPI, "description": "Recommendations retrieved successfully"},
        400: {"model": HTTPErrorResponse, "description": "Invalid user ID"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def get_recommendations(
    session: SessionDep,
    user_id: int = Query(..., description="Telegram User ID"),
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=0),
):
    """
    Get personalized news recommendations for Telegram user
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required"
            )
        
        recommended_news = crud.get_recommendeted_news(session, user_id, limit, page)
        
        result = []
        for item in recommended_news:
            date_str = item.published_at.strftime("%d.%m.%Y") if item.published_at else ""
            
            result.append(NewsResponse(
                id=item.id,
                title=item.title,
                summary=item.summary,
                category=item.category_name,
                source=item.source_name,
                url=item.url,
                date=date_str
            ))

        logger.info(f"Generated {len(result)} recommendations for user {user_id}")
        return create_success_response(
            result=result,
            message="Recommendations retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )