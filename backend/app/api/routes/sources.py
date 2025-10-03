import uuid
from fastapi import APIRouter, Query, HTTPException, status
from typing import List
from app.api.deps import SessionDep
from app import crud
from app.models import SourceResponse, SourceCreate, ResponseAPI, HTTPErrorResponse
from .utils import create_success_response

router = APIRouter(prefix="/sources", tags=["sources"])

@router.get(
    "/", 
    responses={
        200: {"model": ResponseAPI, "description": "Sources retrieved successfully"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def get_sources(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        sources = crud.get_sources(session=session, page=page, limit=limit)
        
        sources_response = [
            SourceResponse(
                id=source.id,
                name=source.name,
                domain=source.domain
            ) for source in sources
        ]
        
        return create_success_response(
            result=sources_response,
            message="Sources retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sources: {str(e)}"
        )

@router.post(
    "/",
    responses={
        200: {"model": ResponseAPI, "description": "Source created successfully"},
        400: {"model": HTTPErrorResponse, "description": "Bad request"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def create_source(
    session: SessionDep,
    source_data: SourceCreate
):
    try:
        source = crud.create_source(session=session, source_create=source_data)
        
        return create_success_response(
            result=SourceResponse(id=source.id, name=source.name, domain=source.domain),
            message="Source created successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating source: {str(e)}"
        )

@router.delete(
    "/{source_id}",
    responses={
        200: {"model": ResponseAPI, "description": "Source deleted successfully"},
        404: {"model": HTTPErrorResponse, "description": "Source not found"},
        500: {"model": HTTPErrorResponse, "description": "Internal server error"}
    }
)
def delete_source(
    session: SessionDep,
    source_id: uuid.UUID
):
    try:
        success = crud.delete_source(session=session, source_id=source_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found"
            )
            
        return create_success_response(
            result=None,
            message="Source deleted successfully"
        )
        
    except HTTPException:
        # Пробрасываем HTTPException как есть
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting source: {str(e)}"
        )