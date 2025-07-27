# بخش: منوها و رابط کاربری
# فایل: submenu_handler.py

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
)
from config import logger
from utils.db import get_db, User
from sqlalchemy.orm import Session

from utils.menu_utils import show_main_menu, load_texts

async def submenu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle submenu selections.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    option = query.data
    logger.info(f"User {user_id} selected submenu option: {option}")

    if option == "cancel_submenu":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Operation cancelled.")
        )
        # Show main menu again
        await show_main_menu(update, context)
        return

    if option == "submenu_profile":
        keyboard = [
            [InlineKeyboardButton(texts.get("submenu_profile_view", "View Profile"), callback_data="submenu_profile_view")],
            [InlineKeyboardButton(texts.get("submenu_profile_edit", "Edit Profile"), callback_data="submenu_profile_edit")],
            [InlineKeyboardButton(texts.get("submenu_back", "Back to Main Menu"), callback_data="cancel_submenu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            texts.get("submenu_prompt", "Please select an option from the submenu:"),
            reply_markup=reply_markup
        )
        return

    if option == "submenu_search":
        keyboard = [
            [InlineKeyboardButton(texts.get("submenu_search_scholarships", "Search Scholarships"), callback_data="submenu_search_scholarships")],
            [InlineKeyboardButton(texts.get("submenu_search_apps", "Search Apps"), callback_data="submenu_search_apps")],
            [InlineKeyboardButton(texts.get("submenu_back", "Back to Main Menu"), callback_data="cancel_submenu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            texts.get("submenu_prompt", "Please select an option from the submenu:"),
            reply_markup=reply_markup
        )
        return

    commands = {
        "submenu_profile_view": "/profile",
        "submenu_profile_edit": "/profile",
        "submenu_search_scholarships": "/search",
        "submenu_search_apps": "/search"
    }

    if option in commands:
        await query.message.reply_text(
            texts.get("submenu_prompt", "Please select an option from the submenu:") + f"\nExecuting {commands[option]}..."
        )
        context.user_data["next_command"] = commands[option]
        update.message.text = commands[option]
        await context.application.process_update(update)
    else:
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )


# Define handlers for main.py
handlers = [
    CallbackQueryHandler(submenu_callback, pattern="^submenu_|^cancel_submenu$")
]