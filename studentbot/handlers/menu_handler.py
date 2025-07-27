# بخش: منوها و رابط کاربری
# فایل: menu_handler.py

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import logger
from utils.db import get_db, User
from sqlalchemy.orm import Session

from utils.menu_utils import show_main_menu, load_texts

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle main menu selections.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    option = query.data
    logger.info(f"User {user_id} selected menu option: {option}")

    if option == "cancel_menu":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Operation cancelled.")
        )
        return

    commands = {
        "menu_profile": "/profile",
        "menu_search": "/search",
        "menu_apps": "/apps",
        "menu_points": "/points",
        "menu_leaderboard": "/leaderboard",
        "menu_question": "/ask",
        "menu_consult": "/consult",
        "menu_weather": "/weather",
        "menu_isee": "/isee",
        "menu_location": "/location",
        "menu_feedback": "/feedback",
        "menu_admin": "/admin",
        "menu_login": "/login"
    }

    if option in commands:
        await query.message.reply_text(
            texts.get("menu_prompt", "Please select an option from the main menu:") + f"\nExecuting {commands[option]}..."
        )
        context.user_data["next_command"] = commands[option]
        # Simulate command execution
        update.message.text = commands[option]
        await context.application.process_update(update)
    else:
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

# Define handlers for main.py
handlers = [
    CommandHandler("menu", show_main_menu),
    CallbackQueryHandler(menu_callback, pattern="^menu_|^cancel_menu$")
]