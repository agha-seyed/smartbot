# بخش: جریان اصلی ربات
# فایل: cmd_start.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import logger
import json
import os

def load_texts(lang: str) -> dict:
    """
    Load language-specific texts from JSON files.

    Args:
        lang (str): Language code (e.g., 'en', 'fa', 'it').

    Returns:
        dict: Language texts or empty dict if file not found.
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command and show language selection menu.
    """
    logger.info(f"User {update.effective_user.id} started the bot.")
    keyboard = [
        [
            InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
            InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa"),
            InlineKeyboardButton("Italiano 🇮🇹", callback_data="lang_it"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select your language / لطفاً زبان خود را انتخاب کنید / Scegli la tua lingua:",
        reply_markup=reply_markup
    )

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle language selection and show welcome message.
    """
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]  # Extract language code (en, fa, it)
    context.user_data["lang"] = lang
    logger.info(f"User {update.effective_user.id} selected language: {lang}")

    texts = load_texts(lang)
    welcome_message = texts.get("welcome_message", "Welcome to Scholarino Bot!")
    await query.message.reply_text(welcome_message, parse_mode="HTML")

    # Trigger main menu (assuming menu_handler is registered)
    from handlers.menu_handler import show_main_menu
    await show_main_menu(update, context)

# Define handlers for main.py
handlers = [
    CommandHandler("start", start),
    CallbackQueryHandler(select_language, pattern="^lang_"),
]
