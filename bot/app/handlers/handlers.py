from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

import app.keyboards as kb
import aiohttp
import asyncio

from app.config.bot_config import ADMIN, API_BASE_URL, TG_KEY_API
import logging


router = Router()

headers = {"api-key": TG_KEY_API}
timeout = aiohttp.ClientTimeout(total=15, connect=10)


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_data = {
        "tg_id": message.from_user.id,
        # "name": message.from_user.full_name,
        "name": message.from_user.full_name,
    }
    async with aiohttp.ClientSession(timeout=timeout) as session:
        response = await session.post(f"{API_BASE_URL}/set_tg_user", json=user_data)
        if response.status != 200:
            await message.answer(f"Ошибка {response.status}.\n\nПопробуйте чуть позже")
        data = await response.json()
    if message.from_user.id == int(ADMIN):  # type: ignore
        await message.answer(f"Hi!\nAdmin {data['name']}", reply_markup=kb.admin_main)
    else:
        await message.answer("Hi!\nI'm a poetry telegram bot", reply_markup=kb.main)


@router.message(Command("random_poem"))
@router.message(F.text.endswith("Случайный стих"))
async def random_poetry(message: Message):
    await message.answer("Подбираю для вас случайный стих...")
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.get(f"{API_BASE_URL}/random_poem", headers=headers)
            if response.status == 200:
                data = await response.json()
                await message.answer(
                    f"{data['author']}\n\n{data['title']}\n\n{data['text']}",
                    reply_markup=await kb.get_favourite_button(),
                )
            else:
                await message.answer(
                    f"Ошибка {response.status}.\n\nПопробуйте чуть позже"
                )
    except asyncio.TimeoutError:
        await message.answer("Сервер долго не отвечает. Попробуйте позже.")
    except aiohttp.ClientError as e:
        await message.answer("Произошла ошибка соединения с сервером.")
        logging.error(f"ERROR ❌ ClientError: {e}")


# Авторские стихи
@router.message(Command("personal_poems"))
@router.message(F.text.endswith("Список ваших авторских стихов"))
async def get_personal_poetry(message: Message):
    user_data = {
        "tg_id": message.from_user.id,
        "name": message.from_user.full_name,
    }
    async with aiohttp.ClientSession(timeout=timeout) as session:
        response = await session.post(
            f"{API_BASE_URL}/get_user_personal_poems",
            headers=headers,
            json=user_data,
        )
        if response.status == 200:
            data = await response.json()
        else:
            return await message.answer("Ошибка при загрузке данных")

    keyboard = await kb.poems(data, page=0, category="pers")
    if keyboard.inline_keyboard:
        await message.answer(
            "Список ваших авторских стихов!",
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            "Пока здесь нет ваших авторских стихов\nДобавьте свой стих.",
            reply_markup=keyboard,
        )


@router.message(F.text.endswith("Авторские стихи"))
async def get_all_personal_poetry(message: Message):
    user_data = {
        "tg_id": message.from_user.id,
        "name": message.from_user.full_name,
    }
    async with aiohttp.ClientSession(timeout=timeout) as session:
        response = await session.post(
            f"{API_BASE_URL}/get_all_personal_poems",
            headers=headers,
            json=user_data,
        )
        if response.status == 200:
            data = await response.json()
        else:
            return await message.answer("Ошибка при загрузке данных")

    keyboard = await kb.poems(data, page=0, category="fav")
    if keyboard.inline_keyboard:
        await message.answer(
            "Список авторских стихов других пользователей!",
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            "Пока здесь нет авторских стихов других пользователей.",
            reply_markup=keyboard,
        )


@router.message(Command("selected_poems"))
@router.message(F.text.endswith("Список избранных стихов"))
async def get_all_poetry(message: Message):
    user_data = {
        "tg_id": message.from_user.id,
        "name": message.from_user.full_name,
    }
    async with aiohttp.ClientSession(timeout=timeout) as session:
        response = await session.post(
            f"{API_BASE_URL}/favorite_poems", headers=headers, json=user_data
        )
        if response.status == 200:
            data = await response.json()

    keyboard = await kb.poems(data, page=0, category="fav")
    if keyboard.inline_keyboard:
        await message.answer(
            "Список ваших избранных стихов!",
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            "Пока здесь нет ваших любимых стихов\nДобавьте понравившийся стих в избранные.",
            reply_markup=keyboard,
        )


@router.callback_query(F.data == "to_favourite")
async def add_poetry(callback: CallbackQuery):
    text = callback.message.text.split("\n")
    user_data = {
        "tg_id": callback.message.chat.id,
        "user_name": callback.from_user.full_name,
        "poem_author": text[0],
        "poem_title": text[2],
        "poem_text": "\n".join(text[4::]),
    }

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/add_poem_to_favorite",
                headers=headers,
                json=user_data,
                timeout=timeout,
            )

        if response.status == 200:
            data = await response.json()
        else:
            return await callback.answer("Ошибка при добавлении в избранное.")

        await callback.answer("Стих добавлен в избранные!")

        new_markup = await kb.get_favourite_button(data["is_favorite"])
        if callback.message.reply_markup != new_markup:
            await callback.message.edit_reply_markup(reply_markup=new_markup)
        # await callback.message.edit_reply_markup(
        # reply_markup=await kb.get_favourite_button(data["is_favorite"])
        # )  # type: ignore[union-attr]
    # except AttributeError:
    except (AttributeError, TelegramBadRequest):
        await callback.message.answer("Увы, вы не можете еще раз добавить этот стих. ❌")  # type: ignore[union-attr]
        await callback.message.delete()
        await callback.answer("")
        return None


@router.callback_query(F.data == "del_favourite")
async def del_poetry(callback: CallbackQuery):
    text = callback.message.text.split("\n")
    user_data = {
        "tg_id": callback.message.chat.id,
        # "user_name": callback.from_user.first_name,
        "user_name": callback.from_user.full_name,
        "poem_author": text[0],
        "poem_title": text[2],
    }
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/del_poem_to_favorite",
                headers=headers,
                json=user_data,
                timeout=timeout,
            )

        if response.status == 200:
            data = await response.json()
        else:
            return await callback.answer("Ошибка при удалении из избранных.")

        await callback.answer("Стих удален из избранных!")

        new_markup = await kb.get_favourite_button(data["is_favorite"])
        if callback.message.reply_markup != new_markup:
            await callback.message.edit_reply_markup(reply_markup=new_markup)
    # except:
    except (AttributeError, TelegramBadRequest):
        await callback.message.answer("Этот стих отсутсвует у вас в избранных. 😢")  # type: ignore[union-attr]
        await callback.message.delete()  # type: ignore[union-attr]
        await callback.answer("")
        return None


@router.callback_query(F.data.startswith("poem_"))
async def poem_info(callback: CallbackQuery):
    tg_id = callback.message.chat.id
    user_name = callback.from_user.full_name
    poem_id = callback.data.split("_")[1]

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/poems",
                headers=headers,
                json={
                    "tg_id": tg_id,
                    "user_name": user_name,
                    "poem_id": poem_id,
                },
                timeout=timeout,
            )

        if response.status == 200:
            data = await response.json()
        else:
            await callback.answer(
                f"Ошибка {response.status}: не удалось получить стих."
            )
            await callback.message.delete()

        await callback.answer("")

        if int(tg_id) == int(ADMIN):
            if data.get('order') is None:
                await callback.message.answer(  # type: ignore[union-attr]
                    f"{data['poem']['author']}\n\n{data['poem']['title']}\n\n{data['poem']['text']}",
                    reply_markup=await kb.get_moderation_keyboard(status=None, poem_id=poem_id),
                ),
            else:
                await callback.message.answer(  # type: ignore[union-attr]
                    f"{data['poem']['author']}\n\n{data['poem']['title']}\n\n{data['poem']['text']}",
                    reply_markup=await kb.get_moderation_keyboard(data['order']['status'], data['order']['poem_id']),
                ),
        else:
            await callback.message.answer(  # type: ignore[union-attr]
                f"{data['poem']['author']}\n\n{data['poem']['title']}\n\n{data['poem']['text']}",
                reply_markup=await kb.get_favourite_button(
                    data["is_favorite"],
                    data["poem"]["is_personal"],
                    data["is_author"],
                    poem_id=poem_id,
                ),
            ),

    except AttributeError:
        await callback.message.answer(
            "Увы, вы не можете больше получить этот стих,\nон был удален. 😢"
        )
    except aiohttp.ClientConnectionError as e:
        logging.error(f"ERROR ❌ Connection error: {e}")
        await callback.message.answer("Ошибка соединения с сервером. Попробуйте позже.")
    except aiohttp.ClientResponseError as e:
        logging.error(f"ERROR ❌ Response error: {e.status} {e.message}")
    except asyncio.TimeoutError:
        logging.error(f"ERROR ❌ Request timeout")
        await callback.message.answer("Сервер не отвечает. Попробуйте позже.")
    except RuntimeError as e:
        logging.error(f"ERROR ❌ Runtime error: {e}")
        await callback.message.answer("Произошла внутренняя ошибка. Попробуйте позже.")

