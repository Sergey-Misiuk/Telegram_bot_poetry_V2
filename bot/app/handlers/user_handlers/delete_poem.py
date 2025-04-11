from aiogram import F, Router
from aiogram.types import CallbackQuery
from app.config.bot_config import API_BASE_URL, TG_KEY_API
import aiohttp
import logging

logger = logging.getLogger(__name__)

router = Router()

headers = {"api-key": TG_KEY_API}
timeout = aiohttp.ClientTimeout(total=15, connect=10)


@router.callback_query(lambda c: c.data.startswith("delete_poem_"))
async def del_poem(callback: CallbackQuery):

    poem_id = int(callback.data.split("_")[2])

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/del_personal_poem",
                headers=headers,
                json={
                    "poem_id": poem_id,
                },
                timeout=timeout,
            )

        if response.status == 200:
            await callback.message.delete()
            await callback.answer("Стих удален")
        else:
            await callback.answer(
                f"Ошибка {response.status}: не удалось получить стих."
            )
    except aiohttp.ClientError as e:
        logger.error(f"Aiohttp error occurred: {e}")
        await callback.answer("Ошибка сети. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")