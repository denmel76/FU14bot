import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from supabase import create_client, Client
import logging

# --- НАСТРОЙКИ (Вставь свои данные) ---
BOT_TOKEN = "9202543767:AAFErNGlNj5v8aTYQqdP9u8HUBxcjSmW-Tc"
SUPABASE_URL = "https://iqvujenjffevijvtdvd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlxdnVqZW5qZmZmZXZqanZ0dmR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE3MzA0OTUsImV4cCI6MjEwNzMwNjQ5NX0.KJNVyRzdB0txk1cwoub_yxNHBVkZNibU9GQc1a5Jnno"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.INFO)

async def get_bot_reply(user_message: str):
    try:
        response = supabase.table('bot_rules') \
            .select('reply_text') \
            .eq('is_active', True) \
            .execute()
        
        for rule in response.data:
            if rule['trigger_word'].lower() in user_message.lower():
                return rule['reply_text']
        return None
    except Exception as e:
        print(f"Ошибка базы: {e}")
        return None

async def log_action(user_id, username, msg_text, bot_reply):
    try:
        supabase.table('bot_logs').insert({
            "user_id": user_id,
            "username": username,
            "message_text": msg_text,
            "bot_reply": bot_reply
        }).execute()
    except Exception as e:
        print(f"Ошибка логов: {e}")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот запущен! Напиши 'привет'.")

@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    reply = await get_bot_reply(user_text)

    if reply:
        await message.answer(reply)
        await log_action(user_id, username, user_text, reply)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
