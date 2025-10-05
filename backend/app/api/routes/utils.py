from fastapi import APIRouter
import uuid
from typing import Any, Optional

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/health-check/")
async def health_check() -> bool:
    return True


def generate_request_id() -> str:
    return str(uuid.uuid4())

def create_success_response(
    result: Any,
    message: str = "Success",
    request_id: Optional[str] = None
) -> dict:
    return {
        "success": True,
        "requestId": request_id or generate_request_id(),
        "message": message,
        "result": result,
        "errors": None
    }