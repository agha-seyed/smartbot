# بخش: فایل‌های زیرساختی
# فایل: config.py

import os
import logging
from logging.handlers import RotatingFileHandler

def validate_env_vars():
    """Validate that all required environment variables are set."""
    required_vars = [
        "BOT_TOKEN",
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

# Validate environment variables at startup
validate_env_vars()

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS", "/etc/secrets/credentials.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Currently unused, reserved for future AI features
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
BASE_URL = os.getenv("BASE_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
QUESTIONS_SHEET_NAME = os.getenv("QUESTIONS_SHEET_NAME")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PORT = int(os.getenv("PORT", 8080))

# Logger setup
logger = logging.getLogger("StudentBot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# File handler (rotating logs to prevent large files)
file_handler = RotatingFileHandler("studentbot.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

def verify_google_creds():
    """Verify that the Google credentials file exists."""
    if not os.path.exists(GOOGLE_CREDS):
        logger.error(f"Google credentials file not found at: {GOOGLE_CREDS}")
        raise FileNotFoundError(f"Google credentials file not found at: {GOOGLE_CREDS}")

# Verify Google credentials at startup
verify_google_creds()
