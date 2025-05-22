# bot start
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN
from handlers import register_handlers

app = Client(
    "mass_mailer_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

register_handlers(app)

print("Bot started...")
app.run()
