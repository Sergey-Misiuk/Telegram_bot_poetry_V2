from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from api.config import DB_URL


# Eсли бы .env был бы в той же папке
# dotenv_path = join(dirname(__file__), ".env")
# load_dotenv(dotenv_path)


if not DB_URL:
    raise ValueError("DATABASE_URL не установлен в .env файле")


engine = create_async_engine(DB_URL, echo=True)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
