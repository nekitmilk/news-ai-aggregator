import uuid
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


def _get_user_or_404(session: SessionDep, user_id: uuid.UUID) -> User:
    """Fetch a user by ID or raise 404."""
    user = session.get(User, user_id)
    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=UsersPublic)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    logger.info(f"Fetching users: skip={skip}, limit={limit}")
    count = session.exec(select(func.count()).select_from(User)).one()
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    logger.info(f"Retrieved {len(users)} users")
    return UsersPublic(data=users, count=count)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    logger.info(f"Creating user: email={user_in.email}")
    existing_user = crud.get_user_by_email(session=session, email=user_in.email)
    if existing_user:
        logger.warning(f"User creation failed: email already exists {user_in.email}")
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    logger.info(f"User created successfully: user_id={user.id}")
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(*, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser) -> Any:
    logger.info(f"Updating current user: user_id={current_user.id}")
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            logger.warning(f"Email conflict when updating user_id={current_user.id}")
            raise HTTPException(status_code=409, detail="User with this email already exists")

    current_user.sqlmodel_update(user_in.model_dump(exclude_unset=True))
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    logger.info(f"User updated successfully: user_id={current_user.id}")
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(*, session: SessionDep, body: UpdatePassword, current_user: CurrentUser) -> Any:
    logger.info(f"Password update attempt: user_id={current_user.id}")
    if not verify_password(body.current_password, current_user.hashed_password):
        logger.warning(f"Incorrect current password: user_id={current_user.id}")
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the current one")

    current_user.hashed_password = get_password_hash(body.new_password)
    session.add(current_user)
    session.commit()
    logger.info(f"Password updated successfully: user_id={current_user.id}")
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    logger.info(f"Fetching current user: user_id={current_user.id}")
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    logger.info(f"Deleting current user: user_id={current_user.id}")
    if current_user.is_superuser:
        logger.warning(f"Superuser attempted to delete self: user_id={current_user.id}")
        raise HTTPException(status_code=403, detail="Super users are not allowed to delete themselves")
    session.delete(current_user)
    session.commit()
    logger.info(f"User deleted successfully: user_id={current_user.id}")
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    logger.info(f"Registering new user: email={user_in.email}")
    existing_user = crud.get_user_by_email(session=session, email=user_in.email)
    if existing_user:
        logger.warning(f"User registration failed: email already exists {user_in.email}")
        raise HTTPException(status_code=400, detail="The user with this email already exists in the system")

    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    logger.info(f"User registered successfully: user_id={user.id}")
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> Any:
    logger.info(f"Fetching user by id: user_id={user_id}, requester_id={current_user.id}")
    user = _get_user_or_404(session, user_id)
    if user != current_user and not current_user.is_superuser:
        logger.warning(f"Insufficient privileges: requester_id={current_user.id}, target_id={user_id}")
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return user


@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def update_user(*, session: SessionDep, user_id: uuid.UUID, user_in: UserUpdate) -> Any:
    logger.info(f"Updating user: user_id={user_id}")
    db_user = _get_user_or_404(session, user_id)
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            logger.warning(f"Email conflict when updating user_id={user_id}")
            raise HTTPException(status_code=409, detail="User with this email already exists")

    updated_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    logger.info(f"User updated successfully: user_id={user_id}")
    return updated_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID) -> Message:
    logger.info(f"Deleting user: user_id={user_id}, requester_id={current_user.id}")
    user = _get_user_or_404(session, user_id)
    if user == current_user:
        logger.warning(f"Superuser attempted to delete self: user_id={user_id}")
        raise HTTPException(status_code=403, detail="Super users are not allowed to delete themselves")

    session.exec(delete(Item).where(col(Item.owner_id) == user_id))
    session.delete(user)
    session.commit()
    logger.info(f"User deleted successfully: user_id={user_id}")
    return Message(message="User deleted successfully")
