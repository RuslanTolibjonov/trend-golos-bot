import asyncio
import subprocess
import tempfile
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile

BOT_TOKEN = "8819485644:AAHg6E4ITngFDKeQCL4EfTAy5em5dNk8TOI"
ADMIN_ID = 7415863796

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

voices = {}
pending = {}

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎙 Barcha goloslar")],
        [KeyboardButton(text="➕ Golos qo‘shish")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("🔥 Trend Golos Bot ishladi!", reply_markup=menu)

@dp.message(F.text == "➕ Golos qo‘shish")
async def add_voice_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Siz admin emassiz.")

    pending[message.from_user.id] = {"step": "wait_media"}
    await message.answer("🎧 Voice, audio yoki video yubor.")

async def convert_to_voice(input_path: str, output_path: str):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vn",
            "-c:a", "libopus",
            "-b:a", "64k",
            output_path
        ],
        check=True
    )

@dp.message(F.voice | F.audio | F.video)
async def receive_media(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("⏳ Qabul qilinyapti...")

    if message.voice:
        file_id = message.voice.file_id

    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            if message.audio:
                tg_file_id = message.audio.file_id
                input_file = temp_dir / "input.mp3"
            else:
                tg_file_id = message.video.file_id
                input_file = temp_dir / "input.mp4"

            output_file = temp_dir / "voice.ogg"

            await bot.download(tg_file_id, destination=input_file)

            await convert_to_voice(str(input_file), str(output_file))

            sent = await bot.send_voice(
                chat_id=ADMIN_ID,
                voice=FSInputFile(output_file),
                caption="✅ Ovoz ajratildi"
            )

            file_id = sent.voice.file_id

    pending[message.from_user.id] = {
        "step": "wait_title",
        "file_id": file_id
    }

    await message.answer("✍️ Endi golos nomini yoz.")

@dp.message(F.text)
async def text_handler(message: Message):
    user_id = message.from_user.id

    if user_id in pending and pending[user_id].get("step") == "wait_title":
        voice_id = len(voices) + 1

        voices[voice_id] = {
            "title": message.text,
            "file_id": pending[user_id]["file_id"],
            "views": 0
        }

        del pending[user_id]

        return await message.answer(f"✅ Saqlandi!\nID: /{voice_id}")

    if message.text == "🎙 Barcha goloslar":
        if not voices:
            return await message.answer("Hozircha golos yo‘q.")

        text = "🎙 Barcha goloslar:\n\n"

        for vid, item in voices.items():
            text += f"/{vid} | {item['title']} | 👁 {item['views']}\n"

        return await message.answer(text)

    if message.text.startswith("/"):
        try:
            voice_id = int(message.text.replace("/", ""))
        except:
            return

        if voice_id not in voices:
            return await message.answer("❌ Bunday golos yo‘q.")

        voices[voice_id]["views"] += 1
        item = voices[voice_id]

        return await message.answer_voice(
            voice=item["file_id"],
            caption=f"🎙 {item['title']}\n👁 {item['views']}"
        )

async def main():
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())