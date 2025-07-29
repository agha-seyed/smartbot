# بخش: منوها و رابط کاربری
# فایل: menu_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from studentbot.config import logger
from studentbot.utils.db import get_db, User
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
    if not user:
        await update.message.reply_text(
            texts.get("no_profile", "Please create your profile first using /profile.")
        )
        return

    keyboard = [
        [InlineKeyboardButton(texts.get("menu_scholarships", "Scholarships"), callback_data="menu_scholarships")],
        [InlineKeyboardButton(texts.get("menu_migration", "Migration"), callback_data="menu_migration")],
        [InlineKeyboardButton(texts.get("menu_housing", "Housing"), callback_data="menu_housing")],
        [InlineKeyboardButton(texts.get("menu_student_life", "Student Life"), callback_data="menu_student_life")],
        [InlineKeyboardButton(texts.get("menu_universities", "Universities"), callback_data="menu_universities")],
        [InlineKeyboardButton(texts.get("menu_language_courses", "Language Courses"), callback_data="menu_language_courses")],
        [InlineKeyboardButton(texts.get("menu_university_news", "University News"), callback_data="menu_university_news")],
        [InlineKeyboardButton(texts.get("menu_tools", "Tools"), callback_data="menu_tools")],
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
    await update.message.reply_text(
        texts.get("menu_prompt", "Please select an option from the main menu:"),
        reply_markup=reply_markup
    )

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
        "menu_scholarships": "/scholarships",
        "menu_migration": "/migration",
        "menu_housing": "/housing",
        "menu_student_life": "/student_life",
        "menu_universities": "/universities",
        "menu_language_courses": "/language_courses",
        "menu_university_news": "/university_news",
        "menu_tools": "/tools",
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
    CommandHandler("start", show_main_menu),  # Override /start to show menu
    CallbackQueryHandler(menu_callback, pattern="^menu_|^cancel_menu$")
]