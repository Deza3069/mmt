# start
from aizen import app
import handlers  # This ensures all handlers are imported and registered

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
    print("Bot is running...")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
