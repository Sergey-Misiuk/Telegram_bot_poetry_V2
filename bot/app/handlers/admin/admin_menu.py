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

from app.config.bot_config import ADMIN, API_BASE_URL, TG_KEY_API


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
async def admin(message: Message):
    keyboard = kb.admin_panel

    await message.answer(
        "Добро пожаловать в админ меню", reply_markup=keyboard
    )


@router.message(IsAdmin(), F.text.endswith("На главную"))
async def to_main_page(message: Message):
    keyboard = kb.admin_main

    await message.answer("Переход в главное меню", reply_markup=keyboard)


@router.message(IsAdmin(), F.text.endswith("Запросы на авторские стихи"))
async def request_order_by_status(message: Message):
    statuses = await fetch_statuses_from_api()
    keyboard = await kb.status_keyboard(statuses)
    await message.answer(
        "Выбирете нужный статус для показа", reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data.startswith("status_"))
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
            await callback.message.answer("Есть стихи")
        else:
            await callback.message.answer(
                "Ошибка: API вернул некорректный статус."
            )
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
        await callback.message.answer(
            "Превышено время ожидания ответа от API."
        )

    except ClientError as e:
        await callback.message.answer(f"Ошибка при запросе: {str(e)}")

    except Exception as e:
        await callback.message.answer("Произошла неизвестная ошибка.")
        print(f"[ERROR] {e}")
