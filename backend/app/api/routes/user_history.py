import uuid
from fastapi import APIRouter, HTTPException, status
from app.api.deps import SessionDep
from app import crud
from app.models import (
    UserHistoryCreate, 
    UserHistoryResponse,  
    ResponseAPI, 
    HTTPErrorResponse
)
from .utils import create_success_response

router = APIRouter(prefix="/user-history", tags=["user-history"])

@router.post(
    "/",
    responses={
        200: {"model": ResponseAPI, "description": "History record created successfully"},
        400: {"model": HTTPErrorResponse, "description": "Bad request"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def create_history_record(
    session: SessionDep,
    history_data: UserHistoryCreate
):
    try:
        history_record = crud.create_user_history(
            session=session, 
            history_create=history_data
        )
        
        return create_success_response(
            result=UserHistoryResponse(
                id=history_record.id,
                user_id=history_record.user_id,
                news_id=history_record.news_id,
                view_timestamp=history_record.view_timestamp
            ),
            message="History record created successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating history record: {str(e)}"
        )

@router.delete(
    "/{history_id}",
    responses={
        200: {"model": ResponseAPI, "description": "History record deleted successfully"},
        404: {"model": HTTPErrorResponse, "description": "History record not found"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def delete_history_record(
    session: SessionDep,
    history_id: uuid.UUID
):
    try:
        success = crud.delete_user_history(
            session=session, 
            history_id=history_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="History record not found"
            )
            
        return create_success_response(
            result=None,
            message="History record deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting history record: {str(e)}"
        )