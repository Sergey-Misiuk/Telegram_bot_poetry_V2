from bs4 import BeautifulSoup
from random import randint, choice
import aiohttp
import re
import logging

from api.models import Poem


async def fetch_html(url):
    """Асинхронный запрос страницы с обработкой ошибок."""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = await response.text()
            return BeautifulSoup(html, "lxml")
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе {url}: {e}")
        return None


async def get_random_poem_url():
    """Выбирает случайную страницу со стихами
    и возвращает ссылку на случайное стихотворение."""
    base_url = "https://www.culture.ru/literature/poems"
    soup = await fetch_html(base_url)
    if not soup:
        return None

    # Находим количество страниц
    pages = soup.find("div", class_="W6UA5").find_all("a", href=True)
    last_page = int(pages[-1]["href"].split("=")[-1])
    random_page = randint(1, last_page)

    # Запрашиваем случайную страницу
    page_url = f"{base_url}?page={random_page}"
    soup = await fetch_html(page_url)
    if not soup:
        return None

    # Получаем список стихотворений на странице
    poem_links = soup.find_all("div", class_="Dx0ke")
    if not poem_links:
        return None

    random_poem = choice(poem_links).find("a", class_="ICocV")
    if not random_poem:
        return None

    return "https://www.culture.ru" + random_poem["href"]


async def parse_poem(url):
    """Парсит страницу стихотворения и возвращает объект Poem."""
    soup = await fetch_html(url)
    if not soup:
        return None

    try:
        # Получаем имя автора и название стиха
        author = soup.select_one("div.HjkFX").get_text(strip=True)
        title = soup.select_one("div.rrWFt").get_text(strip=True)

        # Извлекаем текст стихотворения
        poem_paragraphs = soup.select_one("div.xZmPc")
        # poem_paragraphs = soup.select("div.xZmPc")

        # Очищаем текст от HTML-тегов и соединяем
        poem_text = "\n\n".join(p.get_text("\n", strip=True) for p in poem_paragraphs)

        poem_text = re.sub(
            r"(Следующий стих|Предыдущий стих|Автор.*)",
            "",
            poem_text,
            flags=re.DOTALL,
        ).strip()

        return Poem(author=author, title=title, text=poem_text)

    except AttributeError:
        logging.error(f"Ошибка парсинга данных на {url}")
        return None


async def parser_poetry():
    """Основная функция: выбирает случайное стихотворение и возвращает его."""
    poem_url = await get_random_poem_url()
    if not poem_url:
        return None

    return await parse_poem(poem_url)
