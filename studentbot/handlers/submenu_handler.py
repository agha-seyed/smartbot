# بخش: منوها و رابط کاربری
# فایل: submenu_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
)
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

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the main menu (reused from menu_handler).
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} requested main menu from submenu.")

    db: Session = next(get_db())
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        await update.callback_query.message.reply_text(
            texts.get("no_profile", "Please create your profile first using /profile.")
        )
        return

    keyboard = [
        [InlineKeyboardButton(texts.get("menu_profile", "Profile"), callback_data="submenu_profile")],
        [InlineKeyboardButton(texts.get("menu_search", "Search"), callback_data="submenu_search")],
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

    if context.user_data.get("is_admin", False):
        keyboard.append([InlineKeyboardButton(texts.get("menu_admin", "Admin Panel"), callback_data="menu_admin")])
        keyboard.append([InlineKeyboardButton(texts.get("menu_login", "Admin Login"), callback_data="menu_login")])

    keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        texts.get("menu_prompt", "Please select an option from the main menu:"),
        reply_markup=reply_markup
    )

# Define handlers for main.py
handlers = [
    CallbackQueryHandler(submenu_callback, pattern="^submenu_|^cancel_submenu$")
]