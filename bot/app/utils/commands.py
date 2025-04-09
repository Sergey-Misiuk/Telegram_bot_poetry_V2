from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault
)
from aiogram import Bot


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="random_poem", description="Случайный стих"),
        BotCommand(command="personal_poems", description="Список ваших авторских стихов"),
        BotCommand(command="selected_poems", description="Список избранных стихов"),
        BotCommand(command="start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    
