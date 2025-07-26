# بخش: فایل‌های زیرساختی
# فایل: config.py

# فایل: config.py

import os
import logging
from logging.handlers import RotatingFileHandler

# ✳️ بررسی متغیرهای محیطی
def validate_env_vars():
    required_vars = [
        "TELEGRAM_TOKEN",
        "REDIS_URL",
        "GOOGLE_CREDS",
        "ADMIN_CHAT_ID",
        "BASE_URL",
        "WEBHOOK_SECRET",
        "QUESTIONS_SHEET_NAME",
        "WEATHER_API_KEY",
        "PORT"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

validate_env_vars()

# ✳️ مقداردهی از متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS", "/etc/secrets/credentials.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ممکنه در آینده استفاده شه
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
BASE_URL = os.getenv("BASE_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
QUESTIONS_SHEET_NAME = os.getenv("QUESTIONS_SHEET_NAME")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PORT = int(os.getenv("PORT", 8080))

# ✳️ Logger
logger = logging.getLogger("StudentBot")
logger.setLevel(logging.INFO)

# Console log
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# File log (rotating)
file_handler = RotatingFileHandler("studentbot.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# ✳️ بررسی وجود فایل Google Credentials
def verify_google_creds():
    if not os.path.exists(GOOGLE_CREDS):
        logger.error(f"Google credentials file not found at: {GOOGLE_CREDS}")
        raise FileNotFoundError(f"Google credentials file not found at: {GOOGLE_CREDS}")

verify_google_creds()

