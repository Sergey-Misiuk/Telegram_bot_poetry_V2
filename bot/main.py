import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.handlers import handlers, pagination
from app.handlers.admin import admin_handlers
from app.handlers.user_handlers import create_poem, delete_poem
from app.config.bot_config import BOT_TOKEN

from app.utils.commands import set_commands


all_routers = [
    handlers.router,
    pagination.router,
    admin_handlers.router,
    create_poem.router,
    delete_poem.router,
]


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    
    dp.include_routers(*all_routers)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await set_commands(bot)
    await dp.start_polling(bot)
    

async def startup(dispatcher: Dispatcher):
    print("Starting up...")


async def shutdown(dispatcher: Dispatcher):
    print("Shutting down...")


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
