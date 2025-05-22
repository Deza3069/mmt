from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Pyrogram Client
app = Client("MailerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message()
async def dummy_handler(_, __):  # Required to make bot active
    pass


async def notify_bot_started():
    try:
        await app.send_message(
            chat_id=LOG_CHANNEL,
            text="✅ **Mailer Bot has been started successfully.**"
        )
        logger.info("Startup message sent to log channel.")
    except Exception as e:
        logger.error(f"Failed to send startup message to log channel: {e}")


async def main():
    await app.start()
    logger.info("Bot started.")
    await notify_bot_started()
    await idle()  # Keeps the bot running


if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
