from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

from models.models import Order
from models.models import RequestStatus


# ------------------------- Пользовательские -------------------------


async def add_to_orders(db: AsyncSession, user_id: int, poem_id: int) -> Order:
    """Добавляет новый заказ на публикацию стиха от пользователя."""
    new_order = Order(user_id=user_id, poem_id=poem_id)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order


async def get_personal_poems_by_user(db: AsyncSession, user_id: int) -> List[Order]:
    """Возвращает все авторские стихи пользователя (любой статус)."""
    stmt = select(Order).where(Order.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_all_approved_poems_excluding_user(db: AsyncSession, user_id: int) -> List[Order]:
    """Возвращает все утверждённые авторские стихи, кроме пользователя."""
    stmt = select(Order).where(
        Order.user_id != user_id,
        Order.status == RequestStatus.APPROVED
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_personal_poem_by_id(db: AsyncSession, user_id: int, poem_id: int) -> Optional[Order]:
    """Возвращает заказ по user_id и poem_id."""
    stmt = select(Order).where(
        Order.user_id == user_id,
        Order.poem_id == poem_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ------------------------- Админские -------------------------

async def get_poems_by_status(db: AsyncSession, status: RequestStatus) -> List[Order]:
    """Возвращает все стихи по статусу модерации."""
    stmt = select(Order).where(Order.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_poem_by_status_and_id(
    db: AsyncSession,
    poem_id: int,
    status: Optional[RequestStatus] = None,
) -> Optional[Order]:
    stmt = select(Order).where(Order.poem_id == poem_id)
    
    if status is not None:
        stmt = stmt.where(Order.status == status)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_order_status(
    db: AsyncSession, poem_id: int, new_status: RequestStatus
) -> Optional[Order]:
    """Обновляет статус заказа на стих."""
    stmt = select(Order).where(Order.poem_id == poem_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        return None

    await db.execute(
        update(Order)
        .where(Order.poem_id == poem_id)
        .values(status=new_status)
        .execution_options(synchronize_session="fetch")
    )
    await db.commit()
    await db.refresh(order)

    return order
