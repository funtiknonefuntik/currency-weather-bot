import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
CITY = os.getenv("DIGEST_CITY", "Санкт-Петербург")
DIGEST_TIME= os.getenv("DIGEST_TIME", "7:40")
TZ = os.getenv("DIGEST_TZ", "Europe/Moscow")