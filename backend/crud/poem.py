from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Poem, User, Favourite, Order
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from typing import List, Optional


async def create_poem(
    db: AsyncSession,
    author: str,
    title: str,
    text: str,
    is_personal: bool = False,
) -> Poem | None:
    """Добавляет новый стих в базу данных."""
    new_poem = Poem(
        title=title,
        author=author,
        text=text,
        is_personal=is_personal
    )
    db.add(new_poem)
    try:
        await db.commit()
        return new_poem
    except SQLAlchemyError:
        await db.rollback()
        return None


async def get_poem_by_title(
    db: AsyncSession,
    title: str,
    author: str
) -> Poem | None:
    """Проверяет, существует ли стих с
    таким названием и автором в базе данных."""
    stmt = select(Poem).where(Poem.title == title, Poem.author == author)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_poem_by_poem_id(db: AsyncSession, poem_id: int) -> Poem | None:
    """Проверяет, существует ли стих с таким названием в базе данных."""
    stmt = select(Poem).where(
        Poem.id == poem_id,
    )

    result = await db.execute(stmt)
    poem = result.scalar_one_or_none()

    if poem is None:
        return None

    return poem


async def del_personal_poem(db: AsyncSession, poem_id: int):
    """Удалить авторский стих."""
    stmt = select(Poem).where(Poem.id == poem_id)

    result = await db.execute(stmt)
    poem = result.scalars().first()
    if not poem:
        return False

    await db.delete(poem)

    try:
        await db.commit()
        return True
    except SQLAlchemyError:
        await db.rollback()
        return False
