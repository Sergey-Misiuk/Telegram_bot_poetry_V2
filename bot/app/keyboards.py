from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config.bot_config import ADMIN


main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Случайный стих")],
        [KeyboardButton(text="⭐️ Список избранных стихов")],
        [KeyboardButton(text="📑©️ Авторские стихи")],
        [KeyboardButton(text="📖©️ Список ваших авторских стихов")],
        [KeyboardButton(text="📃 Добавить свой стих")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбирите пункт из меню...",
)



admin_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Случайный стих")],
        [KeyboardButton(text="⭐️ Список избранных стихов")],
        [KeyboardButton(text="📑©️ Авторские стихи")],
        [KeyboardButton(text="📖©️ Список ваших авторских стихов")],
        # [KeyboardButton(text="📃 Добавить свой стих")],
        [KeyboardButton(text="⚙️ Админ панель")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбирите пункт из меню...",
)


admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Статистика количество пользователей")],
        [KeyboardButton(text="📃 test")],
        [KeyboardButton(text="📚 Запросы на авторские стихи")],
        [KeyboardButton(text="⬅️ На главную")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбирите пункт из меню...",
)


async def get_favourite_button(
    is_favorite: bool = False,
    is_personal: bool = False,
    is_author: bool = False,
    poem_id: int = None
):
    keyboard = InlineKeyboardBuilder()

    if is_personal and is_author:
        keyboard.add(
            InlineKeyboardButton(
                # text="🗑 Удалить стих", callback_data="delete_poem"
                text="🗑 Удалить стих", callback_data=f"delete_poem_{poem_id}"
            )
        )
    else:

        text = (
            "🗑 Удалить из избранного"
            if is_favorite
            else "⭐️ Добавить в избранное"
        )
        callback_data = "del_favourite" if is_favorite else "to_favourite"
        keyboard.add(
            InlineKeyboardButton(text=text, callback_data=callback_data)
        )

    return keyboard.adjust(1).as_markup()


async def poems(
    poems, page: int = 0, items_per_page: int = 5, category: str = "fav"
):
    keyboard = InlineKeyboardBuilder()

    total_pages = (len(poems) - 1) // items_per_page + 1
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_items = poems[start_idx:end_idx]

    for poem in page_items:
        if poem is not None:
            title = poem["poem_info"]["title"]
            author = poem["poem_info"]["author"]

            if category == "pers":
                status = poem.get("status", "Неизвестно")
                text = f'{status} "{title}" - {author}'
            else:
                text = f'"{title}" - {author}'

            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"poem_{poem['poem_id']}",
                )
            )

    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⬅ Назад", callback_data=f"{category}_page_{page - 1}"
            )
        )
    if page < total_pages - 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡", callback_data=f"{category}_page_{page + 1}"
            )
        )

    if navigation_buttons:
        keyboard.row(*navigation_buttons)

    return keyboard.adjust(1).as_markup()


async def del_poem():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text="Удалить стих", callback_data="del_poem")
    )

    return keyboard.adjust(1).as_markup()


async def status_keyboard(statuses):
    keyboard = InlineKeyboardBuilder()

    for status in statuses:
        keyboard.add(
            InlineKeyboardButton(
                text=status,
                callback_data=f"status_{status}"
            )
        )
    return keyboard.adjust(1).as_markup()
