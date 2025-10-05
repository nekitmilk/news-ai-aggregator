import uuid
from fastapi import APIRouter, HTTPException, status, Header
from typing import List
from app.api.deps import SessionDep
from app import crud
from app.models import (
    UserFilterResponse, 
    UserFilterCreate, 
    UserFilterUpdate,
    HTTPErrorResponse,
    UserFilterListResponse,
    UserFilterSingleResponse,
    UserFilterIdResponse
)
from .utils import create_success_response

router = APIRouter(prefix="/users/filters", tags=["user_filters"])

@router.get(
    "/",
    response_model=UserFilterListResponse,
    responses={
        200: {"description": "User filters retrieved successfully"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def get_all_user_filters(
    session: SessionDep,
):
    try:
        filters = crud.get_all_user_filters(session=session)
        
        filters_response = [
            UserFilterResponse(
                user_id=filter.user_id,
                category=filter.category,
                source=filter.source,
                search=filter.search,
                start_date=filter.start_date,
                end_date=filter.end_date,
                sort=filter.sort
            ) for filter in filters
        ]
        
        return create_success_response(
            result=filters_response,
            message="User filters retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user filters: {str(e)}"
        )

@router.get(
    "/{user_id}",
    response_model=UserFilterSingleResponse,
    responses={
        200: {"description": "User filters retrieved successfully"},
        404: {"model": HTTPErrorResponse, "description": "User filters not found"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def get_user_filters(
    session: SessionDep,
    user_id: int,
):
    try:
        user_filter = crud.get_user_filter(session=session, user_id=user_id)
        
        if not user_filter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User filters not found"
            )
        
        filter_response = UserFilterResponse(
            user_id=user_filter.user_id,
            category=user_filter.category,
            source=user_filter.source,
            search=user_filter.search,
            start_date=user_filter.start_date,
            end_date=user_filter.end_date,
            sort=user_filter.sort
        )
        
        return create_success_response(
            result=filter_response,
            message="User filters retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user filters: {str(e)}"
        )

@router.post(
    "/",
    response_model=UserFilterIdResponse,
    responses={
        200: {"description": "User filters created successfully"},
        400: {"model": HTTPErrorResponse, "description": "Bad request"},
        422: {"model": HTTPErrorResponse, "description": "Validation error"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def create_user_filter(
    session: SessionDep,
    filter_data: UserFilterCreate,
    user_id: int = Header(..., alias="X-User-ID", description="Telegram User ID")
):
    try:
        # Проверяем, нет ли уже фильтра для этого пользователя
        existing_filter = crud.get_user_filter(session=session, user_id=user_id)
        
        if existing_filter:
            # Если фильтр уже существует, обновляем его
            updated_filter = crud.update_user_filter(
                session=session,
                user_id=user_id,
                filter_update=filter_data
            )
            
            return create_success_response(
                result={"user_id": updated_filter.user_id},
                message="User filters updated successfully"
            )
        
        # Создаем новый фильтр
        filter_obj = crud.create_user_filter(
            session=session, 
            user_id=user_id,
            filter_create=filter_data
        )
        
        return create_success_response(
            result={"user_id": filter_obj.user_id},
            message="User filters created successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_BAD_REQUEST,
            detail=f"Error creating user filters: {str(e)}"
        )

@router.put(
    "/{user_id}",
    response_model=UserFilterIdResponse,
    responses={
        200: {"description": "User filters updated successfully"},
        404: {"model": HTTPErrorResponse, "description": "User filters not found"},
        422: {"model": HTTPErrorResponse, "description": "Validation error"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def update_user_filter(
    session: SessionDep,
    user_id: int,
    filter_data: UserFilterUpdate,
):
    try:
        updated_filter = crud.update_user_filter(
            session=session,
            user_id=user_id,
            filter_update=filter_data
        )
        
        if not updated_filter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User filters not found"
            )
        
        return create_success_response(
            result={"user_id": updated_filter.user_id},
            message="User filters updated successfully"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user filters: {str(e)}"
        )

@router.delete(
    "/{user_id}",
    response_model=UserFilterIdResponse,
    responses={
        200: {"description": "User filters deleted successfully"},
        404: {"model": HTTPErrorResponse, "description": "User filters not found"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def delete_user_filter(
    session: SessionDep,
    user_id: int,
):
    try:
        success = crud.delete_user_filter(session=session, user_id=user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User filters not found"
            )
            
        return create_success_response(
            result={"user_id": user_id},
            message="User filters deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user filters: {str(e)}"
        )