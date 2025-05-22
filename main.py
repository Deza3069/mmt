# main.py

from aizen import app  # Shared Pyrogram Client instance
import handlers.sendmail
import handlers.sudo
import handlers.smtp
import handlers.sendmmail
import handlers.common

from pyrogram import idle
import asyncio
from config import LOG_CHANNEL

async def notify_startup():
    try:
        await app.send_message(LOG_CHANNEL, "✅ Bot has been started.")
    except Exception as e:
        print(f"Startup log failed: {e}")

async def main():
    await app.start()
    await notify_startup()
    print("✅ Bot is running...")
    await idle()  # Keeps the bot alive
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
