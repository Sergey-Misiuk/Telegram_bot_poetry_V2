from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares import IsAdmin

import asyncio
import aiohttp
from aiohttp import (
    ClientError,
    ClientConnectorError,
    ClientResponseError,
    ServerTimeoutError,
)

from app.config.bot_config import API_BASE_URL, TG_KEY_API
from app.middlewares import IsAdmin
import logging


router = Router()

headers = {"api-key": TG_KEY_API}
timeout = aiohttp.ClientTimeout(total=15, connect=10)
# from app.handlers.handlers import router


async def fetch_statuses_from_api():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_BASE_URL}/statuses",
        ) as response:
            if response.status == 200:
                return await response.json()
            return []


@router.message(IsAdmin(), F.text.endswith("Админ панель"))
# @router.message(F.text.endswith("Админ панель"))
async def admin(message: Message):
    keyboard = kb.admin_panel

    await message.answer("Добро пожаловать в админ меню", reply_markup=keyboard)


@router.message(IsAdmin(), F.text.endswith("На главную"))
# @router.message(F.text.endswith("На главную"))
async def to_main_page(message: Message):
    keyboard = kb.admin_main

    await message.answer("Переход в главное меню", reply_markup=keyboard)


@router.message(IsAdmin(), F.text.endswith("Запросы на авторские стихи"))
# @router.message(F.text.endswith("Запросы на авторские стихи"))
async def request_order_by_status(message: Message):
    statuses = await fetch_statuses_from_api()
    keyboard = await kb.status_keyboard(statuses)
    await message.answer("Выбирете нужный статус для показа", reply_markup=keyboard)


@router.callback_query(IsAdmin(), lambda c: c.data.startswith("status_"))
async def handle_status_selection(callback: CallbackQuery):
    status = callback.data.split("_")[1]
    await callback.answer(f"Вы выбрали статус: {status}")
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.get(
                f"{API_BASE_URL}/orders_status_{status}",
                headers=headers,
                timeout=timeout,
                params=None,
            )

        if response.status == 200:
            data = await response.json()
        else:
            await callback.message.answer("Ошибка: API вернул некорректный статус.")

        if data["data"] is not None:
            keyboard = await kb.poems(data, page=0, category="pers")
            await callback.message.answer("Есть стихи", reply_markup=keyboard)
        else:
            await callback.message.answer("Таких стихов пока нет")
    except ClientConnectorError:
        await callback.message.answer(
            "Ошибка подключения к API. Проверьте, запущен ли сервис."
        )

    except ServerTimeoutError:
        await callback.message.answer(
            "Сервер не ответил вовремя. Повторите попытку позже."
        )

    except ClientResponseError as e:
        await callback.message.answer(f"Ошибка ответа от API: {e.status}")

    except asyncio.TimeoutError:
        await callback.message.answer("Превышено время ожидания ответа от API.")

    except ClientError as e:
        await callback.message.answer(f"Ошибка при запросе: {str(e)}")

    except Exception as e:
        await callback.message.answer("Произошла неизвестная ошибка.")
        logging.error(f"ERROR {e}")


@router.callback_query(IsAdmin(), F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery):

    poem_id = int(callback.data.split(":")[1])

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/moderation/approve",
                headers=headers,
                timeout=timeout,
                params=None,
                json={
                    "poem_id": poem_id,
                },
            )

        if response.status == 200:
            data = await response.json()
        else:
            await callback.message.answer("Ошибка: API вернул некорректный статус.")

        if data is not None:
            await callback.answer("Стих одобрен ✅")
        else:
            await callback.message.answer("Такого стиха нет в базе")
    except ClientConnectorError:
        await callback.message.answer(
            "Ошибка подключения к API. Проверьте, запущен ли сервис."
        )


@router.callback_query(IsAdmin(), F.data.startswith("reject:"))
async def handle_reject(callback: CallbackQuery):
    
    poem_id = int(callback.data.split(":")[1])

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/moderation/reject",
                headers=headers,
                timeout=timeout,
                params=None,
                json={
                    "poem_id": poem_id,
                },
            )

        if response.status == 200:
            data = await response.json()
        else:
            await callback.message.answer("Ошибка: API вернул некорректный статус.")

        if data is not None:
            await callback.answer("Стих отклонён ❌")
        else:
            await callback.message.answer("Такого стиха нет в базе")
    except ClientConnectorError:
        await callback.message.answer(
            "Ошибка подключения к API. Проверьте, запущен ли сервис."
        )


@router.callback_query(IsAdmin(), F.data.startswith("to_review:"))
async def handle_to_review(callback: CallbackQuery):

    poem_id = int(callback.data.split(":")[1])

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/moderation/review",
                headers=headers,
                timeout=timeout,
                params=None,
                json={
                    "poem_id": poem_id,
                },
            )

        if response.status == 200:
            data = await response.json()
        else:
            await callback.message.answer("Ошибка: API вернул некорректный статус.")

        if data is not None:
            await callback.answer("Стих возвращён на рассмотрение 🔄")
        else:
            await callback.message.answer("Такого стиха нет в базе")
    except ClientConnectorError:
        await callback.message.answer(
            "Ошибка подключения к API. Проверьте, запущен ли сервис."
        )
