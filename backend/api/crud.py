from sqlalchemy.ext.asyncio import AsyncSession
from .models import Poem, User, Favourite, Order
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from api.config import SECRET_KEY
import jwt


async def create_poem(
    db: AsyncSession,
    author: str,
    title: str,
    text: str,
    is_personal: bool = False,
):
    """Добавляет новый стих в базу данных."""
    new_poem = Poem(
        title=title, author=author, text=text, is_personal=is_personal
    )
    db.add(new_poem)
    try:
        await db.commit()  # Асинхронный коммит изменений
        return new_poem
    except SQLAlchemyError:
        await db.rollback()  # Откат транзакции в случае ошибки
        return None


async def create_user(db: AsyncSession, user_id: int, name: str):
    existing_user = await get_user(db, user_id, name)
    if existing_user:
        return existing_user
    user = User(tg_id=user_id, name=name)
    db.add(user)
    await db.commit()
    return user


async def get_poem_by_title(db: AsyncSession, title: str, author: str):
    """Проверяет, существует ли стих с таким названием и автором в базе данных."""
    # stmt = select(Poem).where(Poem.title == title, Poem.author == author)
    stmt = select(Poem).where(Poem.title == title, Poem.author == author)
    # stmt = select(Poem.__table__).where(
    #     Poem.title == title, Poem.author == author
    # )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_poem_by_poem_id(db: AsyncSession, poem_id: int):
    """Проверяет, существует ли стих с таким названием в базе данных."""
    # stmt = select(Poem).where(Poem.title == title, Poem.author == author)
    stmt = select(Poem).where(
        Poem.id == poem_id,
    )

    result = await db.execute(stmt)
    poem = result.scalar_one_or_none()

    if poem is None:
        return None

    return poem


async def get_user(db: AsyncSession, tg_id: int, name: str):
    """Проверяет, существует ли User в базе данных."""
    # stmt = select(User.__table__).where(
    #     User.tg_id == tg_id, User.name == name
    # )
    stmt = select(User).where(User.tg_id == tg_id, User.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_favorite_poem_by_user(db: AsyncSession, tg_id):
    """Поиск, всех избранных стихов у пользователя."""
    stmt = select(Favourite).where(Favourite.user_id == tg_id)

    result = await db.execute(stmt)
    return result.scalars().all()


async def exiting_favorite_poem_by_user(db: AsyncSession, user_id, poem_id):
    """Поиск, избранный ли стих у пользователя."""
    stmt = select(Favourite).where(
        Favourite.user_id == user_id, Favourite.poem_id == poem_id
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def del_to_favorite(db: AsyncSession, favorite_poem):
    await db.delete(favorite_poem)
    await db.commit()


async def add_to_favorite(db: AsyncSession, user_id: int, poem_id: int):
    new_favorite = Favourite(user_id=user_id, poem_id=poem_id)
    db.add(new_favorite)
    await db.commit()


async def add_to_orders(db: AsyncSession, user_id: int, poem_id: int):
    new_order = Order(user_id=user_id, poem_id=poem_id)
    db.add(new_order)
    await db.commit()


async def get_personal_poems_by_user(db: AsyncSession, user_id):
    """Поиск, всех авторских стихов у пользователя."""
    stmt = select(Order).where(Order.user_id == user_id)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_all_personal_poems(db: AsyncSession, user_id):
    """Поиск, всех авторских стихов."""
    stmt = select(Order).where(Order.user_id != user_id)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_personal_poem_by_id(
    db: AsyncSession, user_id: int, poem_id: int
):
    """Поиск, всех авторских стихов."""
    stmt = select(Order).where(
        Order.user_id == user_id, Order.poem_id == poem_id
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


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


# Admin requests


async def get_all_personal_poem_by_status(db: AsyncSession, status=None):
    stmt = select(Order).where(Order.status.value == status)
    
    orders = await db.execute(stmt)
    result = orders.scalars().all()
    
    if result is not None:
        return result
    return None


async def create_jwt(tg_id: int):
    """Создает JWT-токен для пользователя."""
    return jwt.encode({"tg_id": tg_id}, SECRET_KEY, algorithm="HS256")
