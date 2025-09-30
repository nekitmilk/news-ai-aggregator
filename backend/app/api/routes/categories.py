import uuid
from fastapi import APIRouter, Query, HTTPException, status
from typing import List
from app.api.deps import SessionDep
from app import crud
from app.models import CategoryResponse, CategoryCreate, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get(
    "/",
    responses={
        200: {"model": ResponseAPI, "description": "Categories retrieved successfully"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def get_categories(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        categories = crud.get_categories(session=session, page=page, limit=limit)
        
        categories_response = [
            CategoryResponse(
                id=category.id,
                name=category.name
            ) for category in categories
        ]
        
        return create_success_response(
            result=categories_response,
            message="Categories retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving categories: {str(e)}"
        )

@router.post(
    "/",
    responses={
        200: {"model": ResponseAPI, "description": "Category created successfully"},
        400: {"model": HTTPErrorResponse, "description": "Bad request"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def create_category(
    session: SessionDep,
    category_data: CategoryCreate
):
    try:
        category = crud.create_category(session=session, category_create=category_data)
        
        return create_success_response(
            result=CategoryResponse(id=category.id, name=category.name),
            message="Category created successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating category: {str(e)}"
        )

@router.delete(
    "/{category_id}",
    responses={
        200: {"model": ResponseAPI, "description": "Category deleted successfully"},
        404: {"model": HTTPErrorResponse, "description": "Category not found"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def delete_category(
    session: SessionDep,
    category_id: uuid.UUID
):
    try:
        success = crud.delete_category(session=session, category_id=category_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
            
        return create_success_response(
            result=None,
            message="Category deleted successfully"
        )
        
    except HTTPException:
        # Пробрасываем HTTPException как есть
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )