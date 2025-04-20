import datetime
from enum import Enum as PyEnum
from typing import List, Annotated
from sqlalchemy import (
    BigInteger,
    String,
    ForeignKey,
    Text,
    func,
    Enum,
    Boolean,
)
from sqlalchemy import text as tx
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    backref,
)
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from core.config import DB_URL


engine = create_async_engine(
    DB_URL,
    echo=True,
)

async_session = async_sessionmaker(engine)


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
created_at = Annotated[
    datetime.datetime, mapped_column(server_default=func.now())
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(server_default=func.now(), onupdate=func.now()),
]


class RequestStatus(PyEnum):
    PENDING = "На расмотрении"
    REJECTED = "Отклонён"
    APPROVED = "Одобрен"
    # PENDING = "PENDING"
    # REJECTED = "REJECTED"
    # APPROVED = "APPROVED"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"User(id={self.id}, tg_id={self.tg_id})"


class Poem(Base):
    __tablename__ = "poems"

    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(String(100))
    text: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(500))
    is_personal: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    favourites = relationship(
        "Favourite",
        back_populates="poem_info",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    orders = relationship(
        "Order",
        back_populates="poem_info",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"Poem(title={self.title}, author={self.author}, text={self.text})"
        )


class Favourite(Base):
    __tablename__ = "favourites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    poem_id: Mapped[int] = mapped_column(
        ForeignKey("poems.id", ondelete="CASCADE"), nullable=False
    )

    poem_info = relationship(
        "Poem",
        back_populates="favourites",
        lazy="joined",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Favourite(user_id={self.user_id}, poem_id={self.poem_id})"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    poem_id: Mapped[int] = mapped_column(
        ForeignKey("poems.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.PENDING
    )

    poem_info = relationship(
        "Poem",
        back_populates="orders",
        lazy="joined",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"UserRequest(user_id={self.user_id}, poem_id={self.poem_id} , status={self.status.value})"
        )


async def create_database():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)
