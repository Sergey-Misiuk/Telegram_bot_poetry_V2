from api.models import create_database
from fastapi import FastAPI
from api.endpoints import router as poem_router

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    # Создаём таблицы при старте приложения
    await create_database()


app.include_router(poem_router)
