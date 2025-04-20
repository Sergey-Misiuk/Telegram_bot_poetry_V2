from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Favourite
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional


async def get_favorite_poem_by_user(db: AsyncSession, tg_id: int) -> List[Favourite]:
    """Возвращает все избранные стихи пользователя по его Telegram ID."""
    
    stmt = (
        select(Favourite)
        .options(joinedload(Favourite.poem_info))
        .where(Favourite.user_id == tg_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def exiting_favorite_poem_by_user(db: AsyncSession, user_id: int, poem_id: int) -> Optional[Favourite]:
    """Проверяет, есть ли стих в избранном у пользователя."""
    stmt = select(Favourite).where(
        Favourite.user_id == user_id,
        Favourite.poem_id == poem_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def del_to_favorite(db: AsyncSession, favorite_poem: Favourite) -> None:
    """Удаляет стих из избранного."""
    await db.delete(favorite_poem)
    await db.commit()


async def add_to_favorite(db: AsyncSession, user_id: int, poem_id: int) -> Favourite:
    """Добавляет стих в избранное."""
    new_favorite = Favourite(user_id=user_id, poem_id=poem_id)
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)
    return new_favorite
