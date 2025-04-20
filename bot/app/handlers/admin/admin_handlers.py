from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from app.config.bot_config import API_BASE_URL, HEADERS, TIMEOUT
import app.keyboards as kb
from app.middlewares import IsAdmin
from app.utils.api_helpers import get_to_api, post_to_api
from app.exception import handle_api_errors


router = Router()


@router.message(IsAdmin(), F.text.endswith("Админ панель"))
async def admin(message: Message):
    await message.answer("Добро пожаловать в админ меню", reply_markup=kb.admin_panel)


@router.message(IsAdmin(), F.text.endswith("На главную"))
async def to_main_page(message: Message):
    await message.answer("Переход в главное меню", reply_markup=kb.admin_main)


@router.message(IsAdmin(), F.text.endswith("Статистика количество пользователей"))
async def request_count_users(message: Message):
  
    url = f"{API_BASE_URL}/users/count"
    data = await get_to_api(url, headers=HEADERS, timeout=TIMEOUT)
    
    try:
        if data:
            count = data.get("count", "Неизвестно")
            await message.answer(f"👥 Пользователей всего: {count}")
        else:
            await message.answer("🚫 API вернул ошибку.")
    except Exception as e:
        await handle_api_errors(message, e)


@router.message(IsAdmin(), F.text.endswith("Запросы на авторские стихи"))
async def request_order_by_status(message: Message):
    
    url = f"{API_BASE_URL}/statuses"
    data = await get_to_api(url, headers=HEADERS, timeout=TIMEOUT)
    
    try:
        if data:
            keyboard = kb.status_keyboard(data)
        await message.answer("Выберите статус:", reply_markup=keyboard)
    except Exception as e:
        await handle_api_errors(message, e)


@router.callback_query(IsAdmin(), F.data.startswith("status_"))
async def handle_status_selection(callback: CallbackQuery):
    status = callback.data.split("_", 1)[1]
    await callback.answer(f"Статус: {status}")
    
    url = f"{API_BASE_URL}/orders_status_{status}"
    data = await get_to_api(url, headers=HEADERS, timeout=TIMEOUT)
    
    try:
        if data:
            poems = data.get("data")
            if poems:
                keyboard = kb.poems(poems, page=0, category="pers")
                await callback.message.answer("📜 Стихи:", reply_markup=keyboard)
            else:
                await callback.message.answer("🚫 Нет стихов с этим статусом.")
        else:
            await callback.message.answer("❌ Некорректный статус от API.")
    except Exception as e:
        await handle_api_errors(callback.message, e)


async def update_poem_status(callback: CallbackQuery, status: str, success_msg: str):
    poem_id = int(callback.data.split(":")[1])
    endpoint_map = {
        "APPROVED": "approve",
        "REJECTED": "reject",
        "PENDING": "review"
    }
    json = {"poem_id": poem_id}
    url = f"{API_BASE_URL}/moderation/{endpoint_map[status]}"
    data = await post_to_api(url, data=json, headers=HEADERS, timeout=TIMEOUT)
    
    try:
        if data:
            await callback.answer(success_msg)
        else:
            await callback.message.answer("🚫 Ошибка от API.")
    except Exception as e:
        await handle_api_errors(callback.message, e)


@router.callback_query(IsAdmin(), F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery):
    await update_poem_status(callback, "APPROVED", "✅ Стих одобрен!")


@router.callback_query(IsAdmin(), F.data.startswith("reject:"))
async def handle_reject(callback: CallbackQuery):
    await update_poem_status(callback, "REJECTED", "❌ Стих отклонён!")


@router.callback_query(IsAdmin(), F.data.startswith("to_review:"))
async def handle_to_review(callback: CallbackQuery):
    await update_poem_status(callback, "PENDING", "🔄 Стих возвращён на рассмотрение.")
