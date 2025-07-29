# بخش: Handlerهای اصلی
# فایل: static_info_handler.py

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from studentbot.config import logger
import json

def load_texts(lang: str) -> dict:
    """
    Load language-specific texts from JSON files.
    """
    try:
        with open(f"lang/{lang}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Language file lang/{lang}.json not found.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in lang/{lang}.json.")
        return {}

async def send_static_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a static text message based on the command.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    command = update.message.text.lstrip('/')
    logger.info(f"User {user_id} requested static info for: {command}")

    response_text = texts.get(f"{command}_text", texts.get("under_construction", "This section is under construction."))
    await update.message.reply_text(response_text)

# Define handlers for main.py
handlers = [
    CommandHandler("scholarships", send_static_info),
    CommandHandler("migration", send_static_info),
    CommandHandler("housing", send_static_info),
    CommandHandler("student_life", send_static_info),
    CommandHandler("universities", send_static_info),
    CommandHandler("language_courses", send_static_info),
    CommandHandler("university_news", send_static_info),
    CommandHandler("tools", send_static_info),
]
