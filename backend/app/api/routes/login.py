import logging
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Message, NewPassword, Token, UserPublic
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["login"])


def _get_active_user(session: SessionDep, email: str):
    """Fetch user by email or raise 404."""
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        logger.warning(f"User not found: email={email}")
        raise HTTPException(
            status_code=404, detail="The user with this email does not exist in the system."
        )
    return user


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    logger.info(f"Login attempt: email={form_data.username}")
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(f"Login failed: email={form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        logger.warning(f"Inactive user login attempt: email={form_data.username}")
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(user.id, expires_delta=access_token_expires)
    logger.info(f"Login successful: email={form_data.username}, user_id={user.id}")
    return Token(access_token=token)


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    logger.info(f"Token test: user_id={current_user.id}")
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    logger.info(f"Password recovery requested: email={email}")
    user = _get_active_user(session, email)

    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    logger.info(f"Password recovery email sent: email={email}")
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    logger.info(f"Reset password attempt: token={body.token}")
    email = verify_password_reset_token(token=body.token)
    if not email:
        logger.warning(f"Invalid password reset token: token={body.token}")
        raise HTTPException(status_code=400, detail="Invalid token")

    user = _get_active_user(session, email)
    if not user.is_active:
        logger.warning(f"Inactive user password reset attempt: email={email}")
        raise HTTPException(status_code=400, detail="Inactive user")

    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    logger.info(f"Password updated successfully: user_id={user.id}")
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery (for admins)
    """
    logger.info(f"Password recovery HTML requested: email={email}")
    user = _get_active_user(session, email)

    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    logger.info(f"HTML content generated for email: {email}")
    return HTMLResponse(
        content=email_data.html_content, headers={"subject": email_data.subject}
    )
