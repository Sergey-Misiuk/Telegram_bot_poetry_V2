import logging
import aiohttp
from aiohttp import (
    ClientError,
    ClientConnectorError,
    ServerTimeoutError,
)


async def get_to_api(url: str, headers: dict | None = None, timeout=15) -> dict | None:
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"📬 Запрос к API: {url}, статус: {response.status}")

                if response.status == 200:
                    return await response.json()
                else:
                    logging.warning(f"⚠️ Некорректный статус: {response.status}")
                    return None

    except (ClientConnectorError, ServerTimeoutError) as e:
        logging.error(f"⚠️ Проблема с соединением: {e}")
    except ClientError as e:
        logging.error(f"⚠️ Ошибка клиента: {e}")
    except Exception as e:
        logging.error(f"❌ Неизвестная ошибка: {e}")

    return None


async def post_to_api(url: str, data: dict, headers: dict | None, timeout=15) -> dict | None:
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=data) as response:
                logging.info(f"📤 POST к API: {url}, статус: {response.status}")

                if response.status == 200:
                    return await response.json()
                else:
                    logging.warning(f"⚠️ Некорректный статус: {response.status}")
                    return None

    except (ClientConnectorError, ServerTimeoutError) as e:
        logging.error(f"⚠️ Проблема с соединением: {e}")
    except ClientError as e:
        logging.error(f"⚠️ Ошибка клиента: {e}")
    except Exception as e:
        logging.error(f"❌ Неизвестная ошибка: {e}")

    return None
