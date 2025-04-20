from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import aiohttp
import logging

from app.config.bot_config import API_BASE_URL, TG_KEY_API

import app.states.state as st


router = Router()

headers = {"api-key": TG_KEY_API}
timeout = aiohttp.ClientTimeout(total=15, connect=10)


@router.message(F.text.endswith("Добавить свой стих"))
async def add_poem(message: Message, state: FSMContext):

    await message.answer(
        """Здесь вы можете добавить свой стих,чтобы другие
пользователи могли добавить его к себе.
(не поздно быть поэтом)

Следуйте инструкции состоящей из 3-х этапов:
    1. Введите название вашего стиха.
    2. Введите текст стиха.
    3. Введите имя автора.

После добавления ваш стих будет отправлен на рассмотрение
администратору бота (это необходимо для фильтрации
отправленых стихов, вы сможете видить статус вашего стиха
нажав на /personal_poems
в случае одобрения он появится в разделе 'Список авторских стихов')"""
    )
    await message.answer("Этап №1.\nВведите название стихотворения")
    await state.set_state(st.Reg_poem.title)


@router.message(st.Reg_poem.title)
async def add_poem_first(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(st.Reg_poem.text)
    await message.answer("Этап №2.\nВведите текст стихотворения")


@router.message(st.Reg_poem.text)
async def add_poem_second(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(st.Reg_poem.author)
    await message.answer("Этап №3.\nВведите имя автора")


@router.message(st.Reg_poem.author)
async def add_poem_three(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    data = await state.get_data()

    user_data = {
        "user": {
            "tg_id": message.from_user.id,
            "name": message.from_user.full_name,
        },
        "poem": {
            "author": data["author"],
            "title": data["title"],
            "text": data["text"],
            "is_personal": True,
        },
    }
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(
                f"{API_BASE_URL}/add_personal_poem",
                headers=headers,
                json=user_data,
            )

            if response.status == 200:
                await message.answer("✅ Стих успешно отправлен на рассмотрение.")
            else:
                logging.warning(f"Ошибка API: {response.status}")
                await message.answer("❌ Не удалось отправить стих. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Ошибка при отправке стиха: {e}")
        await message.answer("Произошла внутренняя ошибка. Попробуйте позже.")
    finally:
        await state.clear()