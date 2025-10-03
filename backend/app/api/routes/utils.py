from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True

import uuid
from typing import Any, Optional
from app.models import ErrorResponse

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

def create_error_response(
    message: str = "Error",
    error_code: int = 500,
    request_id: Optional[str] = None
) -> dict:
    return {
        "success": False,
        "requestId": request_id or generate_request_id(),
        "message": message,
        "result": None,
        "errors": {"code": error_code, "message": message}
    }