import asyncio
import logging
from aiohttp import (
    ClientError,
    ClientConnectorError,
    ClientResponseError,
    ServerTimeoutError,
)


async def handle_api_errors(callback_or_msg, e):
    if isinstance(e, ClientConnectorError):
        await callback_or_msg.answer("❗ Ошибка подключения к API.")
        logging.error(f"❌ Error: {e}")
    elif isinstance(e, ServerTimeoutError):
        await callback_or_msg.answer("⏰ Сервер не ответил вовремя.")
        logging.error(f"❌ Error: {e}")
    elif isinstance(e, ClientResponseError):
        await callback_or_msg.answer(f"❌ Ответ API: {e.status}")
        logging.error(f"❌ Error: {e}")
    elif isinstance(e, asyncio.TimeoutError):
        await callback_or_msg.answer("⏳ Таймаут ожидания ответа от API.")
        logging.error(f"❌ Error: {e}")
    elif isinstance(e, ClientError):
        await callback_or_msg.answer(f"⚠ Ошибка запроса: {str(e)}")
        logging.error(f"❌ Error: {e}")
    else:
        logging.error(f"❌ Unknown error: {e}")
        await callback_or_msg.answer("🔧 Ошибка. Попробуйте позже.")