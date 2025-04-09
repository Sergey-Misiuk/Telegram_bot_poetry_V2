from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.keyboards as kb

router = Router()


# @router.callback_query(F.data == "")
# @router.callback_query(F.data == "del_poem")
# async def del_poem(callback: CallbackQuery):
#     item_poem = callback.message.text.split("\n")   # type: ignore[union-attr]
    
#     await rq.delete_poem(item_poem[4])
    
#     keyboard = await kb.personal_poems()
    
#     await callback.answer("Стих удален")
#     await callback.message.delete()   # type: ignore[union-attr]
#     if keyboard.inline_keyboard:
#         await callback.message.answer(  # type: ignore[union-attr]
#             "Список авторский стихов!",
#             reply_markup=keyboard,
#         )
#     else:
#         await callback.message.answer(  # type: ignore[union-attr]
#             "Пока здесь нет авторских стихов\nНо скоро они обязательно появяться.",
#             reply_markup=keyboard,
#         )
