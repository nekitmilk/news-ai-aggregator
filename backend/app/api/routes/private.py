import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models import User, UserPublic

router = APIRouter(tags=["private"], prefix="/private")
logger = logging.getLogger(__name__)


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


def _create_user_instance(user_in: PrivateUserCreate) -> User:
    """Create User instance from input data."""
    hashed_password = get_password_hash(user_in.password)
    return User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
    )


@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """
    Create a new user.
    """
    logger.info(f"Creating new user: email={user_in.email}, full_name={user_in.full_name}")
    try:
        user = _create_user_instance(user_in)
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"User created successfully: user_id={user.id}, email={user.email}")
        return user
    except Exception as e:
        logger.exception(f"Failed to create user: email={user_in.email}")
        raise
