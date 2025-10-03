import uuid
import logging
from fastapi import APIRouter, Query, HTTPException, status
from typing import List
from app.api.deps import SessionDep
from app import crud
from app.models import CategoryResponse, CategoryCreate, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "/",
    response_model=ResponseAPI[List[CategoryResponse]],
    responses={
        500: {"model": HTTPErrorResponse, "description": "Internal server error"},
    },
    summary="Получить список категорий"
)
def get_categories(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
):
    try:
        categories = crud.get_categories(session=session, page=page, limit=limit)
        return create_success_response(
            result=[CategoryResponse(id=c.id, name=c.name) for c in categories],
            message="Categories retrieved successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while retrieving categories (page={page}, limit={limit})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving categories"
        )


@router.post(
    "/",
    response_model=ResponseAPI[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": HTTPErrorResponse, "description": "Bad request"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"},
    },
    summary="Создать категорию"
)
def create_category(
    session: SessionDep,
    category: CategoryCreate,
):
    try:
        created = crud.create_category(session=session, category_create=category)
        return create_success_response(
            result=CategoryResponse(id=created.id, name=created.name),
            message="Category created successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating category: {category.dict()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating category"
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": HTTPErrorResponse, "description": "Category not found"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"},
    },
    summary="Удалить категорию"
)
def delete_category(
    session: SessionDep,
    category_id: uuid.UUID,
):
    try:
        deleted = crud.delete_category(session=session, category_id=category_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        return None
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Error deleting category with id={category_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting category"
        )
