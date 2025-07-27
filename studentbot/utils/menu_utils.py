# بخش: ابزارهای کمکی
# فایل: menu_utils.py

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import logger
from utils.db import get_db, User
from sqlalchemy.orm import Session

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

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the main menu.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} requested main menu.")

    # Check if user has a profile
    db: Session = next(get_db())
    user = db.query(User).filter_by(user_id=user_id).first()

    message_object = update.message or update.callback_query.message

    if not user:
        await message_object.reply_text(
            texts.get("no_profile", "Please create your profile first using /profile.")
        )
        return

    keyboard = [
        [InlineKeyboardButton(texts.get("menu_profile", "Profile"), callback_data="menu_profile")],
        [InlineKeyboardButton(texts.get("menu_search", "Search"), callback_data="menu_search")],
        [InlineKeyboardButton(texts.get("menu_apps", "Apps"), callback_data="menu_apps")],
        [InlineKeyboardButton(texts.get("menu_points", "Points"), callback_data="menu_points")],
        [InlineKeyboardButton(texts.get("menu_leaderboard", "Leaderboard"), callback_data="menu_leaderboard")],
        [InlineKeyboardButton(texts.get("menu_question", "Question"), callback_data="menu_question")],
        [InlineKeyboardButton(texts.get("menu_consult", "Consult"), callback_data="menu_consult")],
        [InlineKeyboardButton(texts.get("menu_weather", "Weather"), callback_data="menu_weather")],
        [InlineKeyboardButton(texts.get("menu_isee", "ISEE"), callback_data="menu_isee")],
        [InlineKeyboardButton(texts.get("menu_location", "Location"), callback_data="menu_location")],
        [InlineKeyboardButton(texts.get("menu_feedback", "Feedback"), callback_data="menu_feedback")]
    ]

    # Add admin options if user is logged in as admin
    if context.user_data.get("is_admin", False):
        keyboard.append([InlineKeyboardButton(texts.get("menu_admin", "Admin Panel"), callback_data="menu_admin")])
        keyboard.append([InlineKeyboardButton(texts.get("menu_login", "Admin Login"), callback_data="menu_login")])

    keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message_object.reply_text(
        texts.get("menu_prompt", "Please select an option from the main menu:"),
        reply_markup=reply_markup
    )
