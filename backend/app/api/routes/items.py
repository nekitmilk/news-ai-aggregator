import uuid
import logging
from typing import Any, Tuple

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["items"])


def _get_item_or_404(session: SessionDep, item_id: uuid.UUID) -> Item:
    """Helper to fetch item or raise 404."""
    item = session.get(Item, item_id)
    if not item:
        logger.warning(f"Item not found: id={item_id}")
        raise HTTPException(status_code=404, detail="Item not found")
    return item


def _check_permissions(item: Item, current_user: CurrentUser) -> None:
    """Raise 400 if current_user has no access to the item."""
    if not current_user.is_superuser and item.owner_id != current_user.id:
        logger.warning(f"Permission denied: user_id={current_user.id}, item_id={item.id}")
        raise HTTPException(status_code=400, detail="Not enough permissions")


def _get_items_query(current_user: CurrentUser) -> Tuple[Any, Any]:
    """Return count query and select query for items based on user role."""
    if current_user.is_superuser:
        count_query = select(func.count()).select_from(Item)
        select_query = select(Item)
    else:
        count_query = select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
        select_query = select(Item).where(Item.owner_id == current_user.id)
    return count_query, select_query


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items with pagination.
    """
    logger.info(f"Fetching items: user_id={current_user.id}, skip={skip}, limit={limit}")
    count_query, select_query = _get_items_query(current_user)
    count = session.exec(count_query).one()
    items = session.exec(select_query.offset(skip).limit(limit)).all()
    logger.info(f"Fetched {len(items)} items (total={count}) for user_id={current_user.id}")
    return ItemsPublic(data=items, count=count)


@router.get("/{item_id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, item_id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    logger.info(f"Fetching item: item_id={item_id}, user_id={current_user.id}")
    item = _get_item_or_404(session, item_id)
    _check_permissions(item, current_user)
    logger.info(f"Item retrieved: item_id={item_id}")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create a new item.
    """
    logger.info(f"Creating item: user_id={current_user.id}, data={item_in.model_dump()}")
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    logger.info(f"Item created: item_id={item.id}, user_id={current_user.id}")
    return item


@router.put("/{item_id}", response_model=ItemPublic)
def update_item(
    *, session: SessionDep, current_user: CurrentUser, item_id: uuid.UUID, item_in: ItemUpdate
) -> Any:
    """
    Update an item.
    """
    logger.info(f"Updating item: item_id={item_id}, user_id={current_user.id}, data={item_in.model_dump(exclude_unset=True)}")
    item = _get_item_or_404(session, item_id)
    _check_permissions(item, current_user)

    update_data = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    logger.info(f"Item updated: item_id={item.id}")
    return item


@router.delete("/{item_id}", response_model=Message)
def delete_item(session: SessionDep, current_user: CurrentUser, item_id: uuid.UUID) -> Message:
    """
    Delete an item.
    """
    logger.info(f"Deleting item: item_id={item_id}, user_id={current_user.id}")
    item = _get_item_or_404(session, item_id)
    _check_permissions(item, current_user)

    session.delete(item)
    session.commit()
    logger.info(f"Item deleted: item_id={item_id}")
    return Message(message="Item deleted successfully")
