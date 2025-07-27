# بخش: جریان اصلی ربات
# فایل: cmd_start.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import logger
import json
import os

from utils.menu_utils import load_texts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    If language is not set, show language selection. Otherwise, show main menu.
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot.")

    if context.user_data.get("lang"):
        from handlers.menu_handler import show_main_menu
        await show_main_menu(update, context)
    else:
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

    # Trigger main menu
    from utils.menu_utils import show_main_menu
    await show_main_menu(query, context)

# Define handlers for main.py
handlers = [
    CommandHandler("start", start),
    CallbackQueryHandler(select_language, pattern="^lang_"),
]
