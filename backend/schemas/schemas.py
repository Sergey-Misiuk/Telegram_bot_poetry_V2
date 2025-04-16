from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from models.models import RequestStatus


# User


class UserSchema(BaseModel):
    tg_id: int = Field(..., example=123456789)
    name: str = Field(..., example="Иван Иванов")
    

# Poem


class PoemSchema(BaseModel):
    id: Optional[int] = Field(None, example=1)
    title: str = Field(..., example="Одиночество")
    author: str = Field(..., example="Михаил Лермонтов")
    text: str = Field(..., example="Поэт умирает в одиночестве...")
    is_personal: Optional[bool] = Field(default=False)

    class Config:
        from_attributes = True
    

class PoemRequest(BaseModel):
    tg_id: int
    user_name: str
    poem_id: int


# Favorite


class FavoriteAddRequest(BaseModel):
    tg_id: int
    user_name: str
    poem_title: str
    poem_author: str
    poem_text: Optional[str] = None


class FavoriteDelRequest(BaseModel):
    tg_id: int
    user_name: str
    poem_title: str
    poem_author: str


class FavouriteSchema(BaseModel):
    id: int
    user_id: int
    poem_id: int
    poem_info: Optional[PoemSchema] = None
    
    
# Personal Poem


class DelPersonalPoem(BaseModel):
    poem_id: int


class PoemStatusUpdate(BaseModel):
    poem_id: int
    
    
# Order


class OrderSchema(BaseModel):
    id: int
    user_id: int
    poem_id: int
    status: RequestStatus

    class Config:
        from_attributes = True
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 42,
                "user_id": 1,
                "poem_id": 7,
                "status": "APPROVED"
            }
        }
        

class PoemDetailSchema(BaseModel):
    poem: PoemSchema
    is_favorite: bool
    is_author: bool
    order: Optional[OrderSchema] = None

    class Config:
        from_attributes = True
