import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_URL = "http://localhost:8000/missions/run"
TOKEN = "ВАШ_ТОКЕН_ТУТ"


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("ברוך הבא! שלח /tfilah לקבל תפילה יומית.")


@dp.message_handler(commands=["tfilah"])
async def tfilah(msg: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json={
            "agent": "poet",
            "objective": "כתוב תפילה קצרה ומחזקת בעברית"
        }) as r:
            data = await r.json()

    await msg.answer(data["result"])
