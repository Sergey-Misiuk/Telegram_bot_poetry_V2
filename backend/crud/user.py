from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Poem, User, Favourite, Order
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from typing import List, Optional


async def create_user(db: AsyncSession, user_id: int, name: str) -> User:
    """Создает пользователя в бд, если он там еще не существует."""
    existing_user = await get_user(db, user_id, name)
    if existing_user:
        return existing_user
    user = User(tg_id=user_id, name=name)
    db.add(user)
    await db.commit()
    return user


async def get_user(db: AsyncSession, tg_id: int, name: str) -> User | None:
    """Проверяет, существует ли User в базе данных."""
    stmt = select(User).where(User.tg_id == tg_id, User.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
