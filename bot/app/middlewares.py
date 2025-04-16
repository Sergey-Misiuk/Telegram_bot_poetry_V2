from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter

from app.config.bot_config import ADMIN


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        if isinstance(event, Message):
            if event.chat.id == int(ADMIN):
                return True
            return False

        elif isinstance(event, CallbackQuery):
            if event.message.chat.id == int(ADMIN):
                return True
            return False

        return False
