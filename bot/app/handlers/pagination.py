from aiogram import Router, types
import aiohttp
import app.keyboards as kb

from app.config.bot_config import API_BASE_URL, TG_KEY_API, API_BASE_URL


router = Router()

headers = {"api-key": TG_KEY_API}
timeout = aiohttp.ClientTimeout(total=15, connect=10)


@router.callback_query(lambda c: c.data.split("_")[0] in ["fav", "pers"])
async def change_page(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    category = parts[0]  # fav или pers
    page = int(parts[2])  # Номер страницы

    user_data = {
        "tg_id": callback.from_user.id,
        "name": callback.from_user.full_name,
    }

    endpoint_map = {
        "fav": "favorite_poems",
        "pers": "get_user_personal_poems",
    }
    endpoint = endpoint_map.get(category)
    if not endpoint:
        return await callback.answer(
            "Ошибка: неизвестная категория", show_alert=True
        )

    async with aiohttp.ClientSession(timeout=timeout) as session:
        response = await session.post(
            f"{API_BASE_URL}/{endpoint}", headers=headers, json=user_data
        )
        if response.status == 200:
            data = await response.json()
        else:
            return await callback.answer(
                "Ошибка при загрузке данных", show_alert=True
            )

    keyboard = kb.poems(data, page=page, category=category)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()
