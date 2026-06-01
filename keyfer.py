import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "8846742326:AAG9S76TOGfEFAxb_hS6skBBrYBJbpezJKA"
API_URL = "https://api.ggsel.com/elastic/goods/query"

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def search_games(query):
    payload = {"search_term": query}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                if not data.get("success"):
                    return []
                return data.get("data", {}).get("items", [])
    except Exception as e:
        print("Ошибка АПИ:", e)
        return []


def filter_steam_keys(items):
    bad_words = ["ps", "playstation", "nintendo", "ps4", "ps5", "xbox", "аккаунт", "account"]
    result = []
    for item in items:
        text = item.get("name", "").lower() + " " + item.get("search_title", "").lower()
        if any(word in text.split() for word in bad_words):
            continue
        result.append(item)
    return result


def build_link(item):
    base = "https://ggsel.net/catalog/product/"
    url_part = item.get("url")
    item_id = item.get("id")

    if url_part:
        return base + url_part.strip("/")

    return base + str(item_id)


def format_items(items):
    if not items:
        return "Ничего не найдено"

    items = sorted(items, key=lambda x: float(x["price_brl"]))[:10]

    text = "🎮 Лучшие Steam ключи:\n\n"
    for item in items:
        name = item["name"]
        price = item["price_brl"]
        seller = item["seller_name"]
        link = build_link(item)
        text += (
            f"🔥 {name}\n"
            f"💰 {price} ₽\n"
            f"🏪 {seller}\n"
            f"🔗 {link}\n\n"
        )

    return text


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Введи название игры, я найду дешёвые Steam/Egs ключи.")


@dp.message()
async def search_handler(message: types.Message):
    query = message.text.strip()
    if not query:
        await message.answer("Напиши название игры")
        return

    await message.answer("Ищу лучшие цены...")

    items = await search_games(query)
    items = filter_steam_keys(items)
    result = format_items(items)

    await message.answer(result)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
