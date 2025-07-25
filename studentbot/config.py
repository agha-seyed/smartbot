import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
SHEET_ID = os.getenv("SHEET_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
BASE_URL = os.getenv("BASE_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
PORT = os.getenv("PORT", 10000)
QUESTIONS_SHEET_NAME = os.getenv("QUESTIONS_SHEET_NAME")

import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
