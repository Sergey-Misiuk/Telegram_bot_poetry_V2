# from http.client import HTTPException
from api import crud
from api.services.parser_func import parser_poetry
from api.services.user_service import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (
    PoemSchema,
    UserSchema,
    UserAuth,
    PoemDetailSchema,
    FavoriteAddRequest,
    FavoriteDelRequest,
    FavoritePoemsSchema,
    FavouriteSchema,
    PersonalPoemSchema,
    PoemRequest,
    DelPersonalPoem,
)
from .models import Poem, User, RequestStatus
from api.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/")
async def read_root():
    return "<h1>Тестовая проверка FastAPI</h1>"


@router.post("/set_tg_user")
async def set_tg_user(user: UserSchema, db: AsyncSession = Depends(get_db)):
    new_user = await crud.create_user(db, user.tg_id, user.name)
    return {
        "message": "User registered",
        "user_id": new_user.id,
        "name": new_user.name,
    }


@router.post("/auth", response_model=UserAuth)
async def auth_user(user: UserSchema, db: AsyncSession = Depends(get_db)):
    existing_user = crud.get_user(db, user.tg_id, user.name)

    if not existing_user:
        new_user = User(tg_id=user.tg_id, name=user.name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    token = crud.create_jwt(user.tg_id)
    return {"token": token}


@router.get("/random_poem", response_model=PoemSchema)
async def get_random_poem(
    db: AsyncSession = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    random_poem = await parser_poetry()
    if random_poem is None:
        raise HTTPException(
            status_code=500, detail="Не удалось получить стихотворение"
        )

    # Проверяем, существует ли стих с таким названием в базе данных
    existing_poem = await crud.get_poem_by_title(
        db, random_poem.title, random_poem.author
    )

    if existing_poem:
        return existing_poem  # Если стих уже есть в базе, возвращаем его

    # Если стих не найден, добавляем новый в базу данных
    new_poem = await crud.create_poem(
        db, random_poem.author, random_poem.title, random_poem.text
    )
    if not new_poem:
        raise HTTPException(
            status_code=500, detail="Ошибка при сохранении стихотворения"
        )

    return new_poem


# @router.post("/favorite_poems", response_model=FavoritePoemsSchema)
@router.post("/favorite_poems", response_model=list[FavouriteSchema])
async def get_fovorite_poems(
    user: UserSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    existing_user = await crud.get_user(db, user.tg_id, user.name)
    favorite_poems = await crud.get_favorite_poem_by_user(db, existing_user.id)

    if favorite_poems is None:
        return None
    return favorite_poems


@router.post("/poems", response_model=PoemDetailSchema)
async def get_poem(
    request: PoemRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    poem = await crud.get_poem_by_poem_id(db, request.poem_id)
    if poem is None:
        raise HTTPException(status_code=404, detail="Стихотворение не найдено")

    user = await crud.get_user(db, request.tg_id, request.user_name)
    is_favorite = await crud.exiting_favorite_poem_by_user(
        db, user.id, request.poem_id
    )

    personal_poem = await crud.get_personal_poem_by_id(
        db, user.id, request.poem_id
    )

    return PoemDetailSchema(
        poem=poem,
        is_favorite=is_favorite is not None,
        is_author=personal_poem is not None,
    )


@router.post("/del_poem_to_favorite", response_model=PoemDetailSchema)
async def delete_poem_to_favorite(
    request: FavoriteDelRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    existing_poem = await crud.get_poem_by_title(
        db, request.poem_title, request.poem_author
    )

    user = await crud.get_user(db, request.tg_id, request.user_name)
    is_favorite = await crud.exiting_favorite_poem_by_user(
        db, user.id, existing_poem.id
    )

    if is_favorite:
        await crud.del_to_favorite(db, is_favorite)
        return PoemDetailSchema(
            poem=existing_poem, is_favorite=False, is_author=False
        )
    return PoemDetailSchema(
        poem=existing_poem, is_favorite=True, is_author=False
    )


@router.post("/add_poem_to_favorite")
async def add_poem_to_favorite(
    request: FavoriteAddRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    existing_poem = await crud.get_poem_by_title(
        db, request.poem_title, request.poem_author
    )
    if existing_poem is None:
        existing_poem = await crud.create_poem(
            db, request.poem_author, request.poem_title, request.poem_text
        )

    user = await crud.get_user(db, request.tg_id, request.user_name)
    is_favorite = await crud.exiting_favorite_poem_by_user(
        db, user.id, existing_poem.id
    )

    if is_favorite:
        return PoemDetailSchema(
            poem=existing_poem, is_favorite=False, is_author=False
        )
    await crud.add_to_favorite(db, user.id, existing_poem.id)
    return PoemDetailSchema(
        poem=existing_poem, is_favorite=True, is_author=False
    )


@router.post("/add_personal_poem")
async def add_personal_poem(
    # request: PersonalPoemSchema,
    user: UserSchema,
    poem: PoemSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    personal_poem = await crud.create_poem(
        db, poem.author, poem.title, poem.text, is_personal=True
    )
    user_db = await crud.get_user(db, user.tg_id, user.name)
    await crud.add_to_orders(db, user_id=user_db.id, poem_id=personal_poem.id)


@router.post("/get_user_personal_poems")
async def get_personal_poems(
    user: UserSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    existing_user = await crud.get_user(db, user.tg_id, user.name)
    favorite_poems = await crud.get_personal_poems_by_user(
        db, existing_user.id
    )

    if favorite_poems is None:
        return None
    return favorite_poems


@router.post("/get_all_personal_poems")
async def get_all_personal_poems(
    user: UserSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    existing_user = await crud.get_user(db, user.tg_id, user.name)
    all_personal_poems = await crud.get_all_personal_poems(
        db, existing_user.id
    )

    if all_personal_poems is None:
        return None
    return all_personal_poems


@router.post("/del_personal_poem")
async def del_personal_poem(
    request: DelPersonalPoem,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    await crud.del_personal_poem(db, request.poem_id)
    return True


# Admin endpoint


@router.get("/statuses")
async def get_request_statuses():
    return [status.value for status in RequestStatus]


@router.get("/orders_status_{status}")
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),

):
    return "Succsess"
