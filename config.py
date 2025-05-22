import os

API_ID = int(os.getenv("API_ID", 12345))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
MONGO_URI = os.getenv("MONGO_URI", "your_mongodb_uri")
OWNER_ID = int(os.getenv("OWNER_ID", 123456789))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", -1001234567890))
