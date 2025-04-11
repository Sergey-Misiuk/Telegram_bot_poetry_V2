from pydantic import BaseModel
from typing import List, Any


class PoemSchema(BaseModel):
    author: str
    title: str
    text: str
    is_personal: bool

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    tg_id: int
    name: str


class UserAuth(BaseModel):
    token: str


class Order(BaseModel):
    user_id: int
    poem_id: int
    status: str

    class Config:
        from_attributes = True


class PoemDetailSchema(BaseModel):
    poem: PoemSchema
    is_favorite: bool
    is_author: bool
    order: Order | None


class FavouriteSchema(BaseModel):
    user_id: int
    poem_id: int
    poem_info: PoemSchema

    class Config:
        from_attributes = True


class FavoritePoemsSchema(BaseModel):
    favorite_poems: List[FavouriteSchema]


class FavoriteAddRequest(BaseModel):
    tg_id: int
    user_name: str
    poem_title: str
    poem_author: str
    poem_text: str


class FavoriteDelRequest(BaseModel):
    tg_id: int
    user_name: str
    poem_title: str
    poem_author: str


class PoemRequest(BaseModel):
    tg_id: int
    user_name: str
    poem_id: int


class PersonalPoemSchema(BaseModel):
    # tg_id: int
    # user_name: str
    user: UserSchema


class DelPersonalPoem(BaseModel):
    # tg_id: int
    poem_id: int


class PoemStatusUpdate(BaseModel):
    poem_id: int
