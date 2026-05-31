import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8819485644:AAHg6E4ITngFDKeQCL4EfTAy5em5dNk8TOI")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🔥 Trend Golos Bot ishga tushdi!\n\n"
        "Tez orada trend ovozlar qo'shiladi."
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())