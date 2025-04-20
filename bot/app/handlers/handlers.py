from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

import app.keyboards as kb
from app.config.bot_config import ADMIN, API_BASE_URL, HEADERS, TIMEOUT
from app.utils.api_helpers import get_to_api, post_to_api
from app.exception import handle_api_errors


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_data = {
        "tg_id": message.from_user.id,
        "name": message.from_user.full_name,
    }
    url = f"{API_BASE_URL}/set_tg_user"
    data = await post_to_api(url, data=user_data, headers=HEADERS, timeout=TIMEOUT)

    if not data:
        return await message.answer("Произошла ошибка. Попробуйте позже.")

    if message.from_user.id == int(ADMIN):  # type: ignore
        await message.answer(f"Hi!\nAdmin {data['name']}", reply_markup=kb.admin_main)
    else:
        await message.answer("Hi!\nI'm a poetry telegram bot", reply_markup=kb.main)


@router.message(Command("random_poem"))
@router.message(F.text.endswith("Случайный стих"))
async def random_poetry(message: Message):
    await message.answer("Подбираю для вас случайный стих...")

    url = f"{API_BASE_URL}/random_poem"
    data = await get_to_api(url, headers=HEADERS, timeout=TIMEOUT)

    try:
        if data:
            await message.answer(
                f"{data['author']}\n\n{data['title']}\n\n{data['text']}",
                reply_markup=kb.get_favourite_button(),
            )
        else:
            return await message.answer("Ошибка при получении стиха. Попробуйте позже.")
    except Exception as e:
        await handle_api_errors(message, e)


@router.message(Command("personal_poems"))
@router.message(F.text.endswith("Список ваших авторских стихов") | (F.text == "/Мои стихи"))
async def get_personal_poetry(message: Message):
    user_data = {"tg_id": message.from_user.id, "name": message.from_user.full_name}

    url = f"{API_BASE_URL}/get_user_personal_poems"
    data = await post_to_api(url, data=user_data, headers=HEADERS, timeout=TIMEOUT)

    keyboard = kb.poems(data or [], page=0, category="pers")
    if keyboard.inline_keyboard:
        await message.answer("Список ваших авторских стихов!", reply_markup=keyboard)
    else:
        await message.answer("Пока нет авторских стихов. Добавьте свой стих.", reply_markup=keyboard)


@router.message(F.text.endswith("Авторские стихи"))
async def get_all_personal_poetry(message: Message):
    user_data = {
        "tg_id": message.from_user.id,
        "name": message.from_user.full_name
    }

    url = f"{API_BASE_URL}/get_all_personal_poems"
    data = await post_to_api(url, data=user_data, headers=HEADERS, timeout=TIMEOUT)
    
    keyboard = kb.poems(data or [], page=0, category="fav")
    if keyboard.inline_keyboard:
        await message.answer("Авторские стихи других пользователей!", reply_markup=keyboard)
    else:
        await message.answer("Пока таких стихов нет.")


@router.message(Command("selected_poems"))
@router.message(F.text.endswith("Список избранных стихов"))
async def get_favorites(message: Message):
    user_data = {
        "tg_id": message.from_user.id,
        "name": message.from_user.full_name
    }

    url = f"{API_BASE_URL}/favorite_poems"
    data = await post_to_api(url, data=user_data, headers=HEADERS, timeout=TIMEOUT)
    
    keyboard = kb.poems(data or [], page=0, category="fav")
    if keyboard.inline_keyboard:
        await message.answer("Ваши избранные стихи:", reply_markup=keyboard)
    else:
        await message.answer("Избранных стихов пока нет.")


@router.callback_query(F.data == "to_favourite")
async def add_to_favourite(callback: CallbackQuery):
    text = callback.message.text.split("\n")
    user_data = {
        "tg_id": callback.message.chat.id,
        "user_name": callback.from_user.full_name,
        "poem_author": text[0],
        "poem_title": text[2],
        "poem_text": "\n".join(text[4:]),
    }

    url = f"{API_BASE_URL}/favorite/add"
    data = await post_to_api(url, data=user_data, headers=HEADERS, timeout=TIMEOUT)
    
    if not data:
        return await callback.answer("⚠️ Ошибка при добавлении в избранное.")

    await callback.answer("⭐️ Стих добавлен в избранное!")

    new_markup = kb.get_favourite_button(data["is_favorite"])
    try:
        await callback.message.edit_reply_markup(reply_markup=new_markup)
    except TelegramBadRequest:
        await callback.message.delete()


@router.callback_query(F.data == "del_favourite")
async def del_from_favourite(callback: CallbackQuery):
    text = callback.message.text.split("\n")
    user_data = {
        "tg_id": callback.message.chat.id,
        "user_name": callback.from_user.full_name,
        "poem_author": text[0],
        "poem_title": text[2],
    }

    url = f"{API_BASE_URL}/favorite/remove"
    data = await post_to_api(url, data=user_data, headers=HEADERS, timeout=TIMEOUT)
    
    if not data:
        return await callback.answer("⚠️ Ошибка при удалении из избранных.")

    await callback.answer("🗑 Удалено из избранных.")

    new_markup = kb.get_favourite_button(data["is_favorite"])
    try:
        await callback.message.edit_reply_markup(reply_markup=new_markup)
    except TelegramBadRequest:
        await callback.message.delete()


@router.callback_query(F.data.startswith("poem_"))
async def poem_info(callback: CallbackQuery):
    poem_id = callback.data.split("_")[1]
    user_data = {
        "tg_id": callback.message.chat.id,
        "user_name": callback.from_user.full_name,
        "poem_id": poem_id,
    }

    url = f"{API_BASE_URL}/poems"
    data = await post_to_api(url, data=user_data, headers=HEADERS, timeout=TIMEOUT)
    
    if not data:
        await callback.answer("⚠️ Ошибка при получении стиха.")
        await callback.message.delete()
        return

    await callback.answer("")
    markup = (
        kb.get_moderation_keyboard(data["order"]["status"], data["order"]["poem_id"])
        if callback.from_user.id == int(ADMIN) and data.get("order")
        else (
            kb.get_moderation_keyboard(None, poem_id)
            if callback.from_user.id == int(ADMIN)
            else kb.get_favourite_button(
                data["is_favorite"],
                data["poem"]["is_personal"],
                data["is_author"],
                poem_id=poem_id,
            )
        )
    )
    await callback.message.answer(
        f"{data['poem']['author']}\n\n{data['poem']['title']}\n\n{data['poem']['text']}",
        reply_markup=markup,
    )
