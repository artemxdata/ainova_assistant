# app/bot/telegram_bot.py

import asyncio
from typing import Dict, List

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart


from app.config import TELEGRAM_BOT_TOKEN
from app.llm_client import ask_llm, DEFAULT_SYSTEM_PROMPT

from app.agent import run_ainova_agent

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не найден. Заполни его в .env")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "Привет! Я AI-ассистент студии AINOVA 🧠✨\n\n"
        "Пиши мне вопросы — я буду отвечать и немного запоминать контекст."
    )
    await message.answer(text)


@dp.message()
async def handle_message(message: Message):
    user_text = message.text or ""
    tg_user = message.from_user

    # Временное сообщение, чтобы показать, что бот думает
    thinking_msg = await message.answer("Думаю над ответом... 🤔")

    # Вызываем единый "мозг" ассистента
    answer = await run_ainova_agent(
        user_external_id=tg_user.id,
        username=tg_user.username,
        user_text=user_text,
    )

    await thinking_msg.edit_text(answer)

async def main():
    print("AINOVA Telegram-бот запущен. Нажми Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())