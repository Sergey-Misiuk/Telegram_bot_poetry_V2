from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter
from app.keyboards import admin_main, main

from typing import Callable, Dict, Any, Awaitable

from app.config.bot_config import ADMIN

# acsees = ('Админ панель', 'На главную', 'Добавить стих')
# acsees = ('Админ панель', 'На главную',)


class AccessMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # data['event_update'].message.text.endswith(acsees)
        if event.chat.id == int(ADMIN):
            # return await event.answer('Приветствую, Админ!',reply_markup=admin_main)
            await event.answer('Привет, Админ!', reply_markup=admin_main)
            return await handler(event, data)
        else:
            # event.reply_markup = test
            # data['event_update'].message.reply_markup = test
            await event.answer(f'{data["event_update"].message.text}', reply_markup=main)
            return await handler(event, data)


# class IsAdmin(BaseFilter):
#     async def __call__(self, handler, event, data):
#         if isinstance(event, Message):
#             # Для сообщений
#             if event.chat.id != int(ADMIN):
#                 await event.answer("У вас нет прав для выполнения этой операции.")
#                 return
#         elif isinstance(event, CallbackQuery):
#             # Для callback-запросов
#             if event.message.chat.id != int(ADMIN):
#                 await event.answer("У вас нет прав для выполнения этой операции.")
#                 return
        
#         return await handler(event, data)

# class IsAdmin(BaseFilter):
#     async def __call__(self, event: Message | CallbackQuery) -> bool:
#         if isinstance(event, Message):
#             await event.answer("У вас нет прав для выполнения этой операции.")
#             return event.chat.id == int(ADMIN)
#         elif isinstance(event, CallbackQuery):
#             await event.answer("У вас нет прав для выполнения этой операции.")
#             return event.message.chat.id == int(ADMIN)
#         return False

class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        print()
        print()
        print(f"[IsAdmin] called for event: {event}")
        print()
        print()
        if isinstance(event, Message):
            if event.chat.id != int(ADMIN):
                await event.answer("У вас нет прав для выполнения этой операции.")
                return False
            return True

        elif isinstance(event, CallbackQuery):
            if event.message.chat.id != int(ADMIN):
                await event.answer("У вас нет прав для выполнения этой операции.")
                return False
            return True

        return False