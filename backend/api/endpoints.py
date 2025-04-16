# from http.client import HTTPException
import crud
from api.utils.parser_func import parser_poetry
from api.utils.security import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import (
    PoemSchema,
    UserSchema,
    PoemDetailSchema,
    FavoriteAddRequest,
    FavoriteDelRequest,
    FavouriteSchema,
    PoemRequest,
    DelPersonalPoem,
    PoemStatusUpdate,
)
from models.models import RequestStatus
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", summary="Тестовый эндпоинт")
async def read_root() -> str:
    return "Тестовая проверка FastAPI"


@router.post("/set_tg_user", summary="Регистрация пользователя")
async def set_tg_user(user: UserSchema, db: AsyncSession = Depends(get_db)):
    new_user = await crud.create_user(db, user.tg_id, user.name)
    return {
        "message": "User registered",
        "user_id": new_user.id,
        "name": new_user.name,
    }


@router.get("/random_poem", response_model=PoemSchema, summary="Случайный стих")
async def get_random_poem(
    db: AsyncSession = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    random_poem = await parser_poetry()
    if random_poem is None:
        raise HTTPException(status_code=500, detail="Не удалось получить стихотворение")

    existing_poem = await crud.get_poem_by_title(
        db, random_poem.title, random_poem.author
    )

    if existing_poem:
        return existing_poem

    new_poem = await crud.create_poem(
        db, random_poem.author, random_poem.title, random_poem.text
    )
    if not new_poem:
        raise HTTPException(
            status_code=500, detail="Ошибка при сохранении стихотворения"
        )

    return new_poem


@router.post("/favorite_poems", response_model=list[FavouriteSchema], summary="Список избранного")
async def get_fovorite_poems(
    user: UserSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> list[FavouriteSchema]:
    existing_user = await crud.get_user(db, user.tg_id, user.name)
    favorite_poems = await crud.get_favorite_poem_by_user(db, existing_user.id)

    return favorite_poems or []


@router.post("/poems", response_model=PoemDetailSchema, summary="Получить конкретный стих")
async def get_poem(
    request: PoemRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    poem = await crud.get_poem_by_poem_id(db, request.poem_id)
    if poem is None:
        raise HTTPException(status_code=404, detail="Стихотворение не найдено")

    user = await crud.get_user(db, request.tg_id, request.user_name)
    is_favorite = await crud.exiting_favorite_poem_by_user(db, user.id, request.poem_id)

    personal_poem = await crud.get_personal_poem_by_id(db, user.id, request.poem_id)
    order = await crud.get_poem_by_status_and_id(db, poem_id=request.poem_id)

    return PoemDetailSchema(
        poem=poem,
        is_favorite=is_favorite is not None,
        is_author=personal_poem is not None,
        order=order,
    )


@router.post("/favorite/remove", response_model=PoemDetailSchema, summary="Удалить из избранного")
async def delete_poem_to_favorite(
    request: FavoriteDelRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    poem = await crud.get_poem_by_title(
        db, request.poem_title, request.poem_author
    )

    user = await crud.get_user(db, request.tg_id, request.user_name)
    is_favorite = await crud.exiting_favorite_poem_by_user(
        db, user.id, poem.id
    )

    if is_favorite:
        await crud.del_to_favorite(db, is_favorite)
        return PoemDetailSchema(poem=poem, is_favorite=False, is_author=False, order=None)
    return PoemDetailSchema(poem=poem, is_favorite=True, is_author=False, order=None)


@router.post("/favorite/add", response_model=PoemDetailSchema, summary="Добавить в избранное")
async def add_poem_to_favorite(
    request: FavoriteAddRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    poem = await crud.get_poem_by_title(
        db, request.poem_title, request.poem_author
    )
    if poem is None:
        poem = await crud.create_poem(
            db, request.poem_author, request.poem_title, request.poem_text
        )

    user = await crud.get_user(db, request.tg_id, request.user_name)
    is_favorite = await crud.exiting_favorite_poem_by_user(
        db, user.id, poem.id
    )

    if is_favorite:
        return PoemDetailSchema(poem=poem, is_favorite=False, is_author=False, order=None)
    await crud.add_to_favorite(db, user.id, poem.id)
    return PoemDetailSchema(poem=poem, is_favorite=True, is_author=False, order=None)


@router.post("/add_personal_poem", summary="Добавить авторский стих")
async def add_personal_poem(
    user: UserSchema,
    poem: PoemSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    personal_poem = await crud.create_poem(
        db, poem.author, poem.title, poem.text, is_personal=True
    )
    user_db = await crud.get_user(db, user.tg_id, user.name)
    result = await crud.add_to_orders(db, user_id=user_db.id, poem_id=personal_poem.id)
    
    return {"message": "success", "data": result}


@router.post("/get_user_personal_poems", summary="Авторские стихи пользователя")
async def get_personal_poems(
    user: UserSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    existing_user = await crud.get_user(db, user.tg_id, user.name)
    favorite_poems = await crud.get_personal_poems_by_user(db, existing_user.id)

    return favorite_poems or []


@router.post("/get_all_personal_poems", summary="Одобренные авторские стихи (без своих)")
async def get_all_personal_poems(
    user: UserSchema,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    existing_user = await crud.get_user(db, user.tg_id, user.name)

    return await crud.get_all_approved_poems_excluding_user(db, existing_user.id)


@router.post("/del_personal_poem", summary="Удалить авторский стих")
async def del_personal_poem(
    request: DelPersonalPoem,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    await crud.del_personal_poem(db, request.poem_id)
    return {"message": "Deleted"}


# Admin endpoint


@router.get("/statuses")
async def get_request_statuses():
    return [status.value for status in RequestStatus]


@router.get("/orders_status_{status}", summary="Все стихи по статусу")
async def get_all_orders(
    status: RequestStatus,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    result = await crud.get_poems_by_status(db, status=status)

    if result is not None:
        return {"data": result, "message": "Succsess"}
    return {"data": result, "message": "Faild"}


@router.post("/moderation/approve")
async def approve_poem(data: PoemStatusUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.update_order_status(db, data.poem_id, "APPROVED")


@router.post("/moderation/review")
async def send_to_review(data: PoemStatusUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.update_order_status(db, data.poem_id, "PENDING")


@router.post("/moderation/reject")
async def reject_poem(data: PoemStatusUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.update_order_status(db, data.poem_id, "REJECTED")
