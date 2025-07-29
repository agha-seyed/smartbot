# بخش: قابلیت‌های اضافی
# فایل: apps_guide_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)
from studentbot.config import logger, ADMIN_CHAT_ID
from studentbot.utils.gsheets import append_to_sheet
from studentbot.utils.db import get_db, User
from studentbot.handlers.gamification_handler import add_points
from sqlalchemy.orm import Session
from datetime import datetime
import json

# States for ConversationHandler
CATEGORY, APP = range(2)

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

def load_apps() -> dict:
    """
    Load apps data from apps.json.

    Returns:
        dict: Apps data or empty dict if file not found.
    """
    try:
        with open("apps.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Apps file apps.json not found.")
        return {"categories": []}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in apps.json.")
        return {"categories": []}

async def start_apps_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the apps guide process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started apps guide.")

    # Check if user has a profile
    db: Session = next(get_db())
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        await update.message.reply_text(
            texts.get("no_profile", "Please create your profile first using /profile.")
        )
        return ConversationHandler.END

    context.user_data["user_profile"] = {
        "first_name": user.first_name,
        "family_name": user.family_name,
        "age": user.age,
        "email": user.email,
        "field_of_study": user.field_of_study,
        "country": user.country
    }

    # Load apps data
    apps_data = load_apps()
    if not apps_data["categories"]:
        await update.message.reply_text(
            texts.get("error_message", "No apps available at the moment. Please try again later.")
        )
        return ConversationHandler.END

    # Create category buttons
    keyboard = [
        [InlineKeyboardButton(category["display_name"][lang], callback_data=f"category_{category['name']}")]
        for category in apps_data["categories"]
    ]
    keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_apps")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("apps_intro", "Please select a category of apps:"),
        reply_markup=reply_markup
    )
    return CATEGORY

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the category selection and show apps.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    callback_data = query.data

    if callback_data == "cancel_apps":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Apps guide cancelled.")
        )
        context.user_data.pop("user_profile", None)
        return ConversationHandler.END

    category_name = callback_data.split("_")[1]
    apps_data = load_apps()
    category = next((cat for cat in apps_data["categories"] if cat["name"] == category_name), None)
    if not category:
        await query.message.reply_text(
            texts.get("error_message", "Invalid category. Please try again.")
        )
        return CATEGORY

    context.user_data["selected_category"] = category_name
    logger.info(f"User {user_id} selected category: {category_name}")

    # Create app buttons
    keyboard = [
        [InlineKeyboardButton(app["name"], callback_data=f"app_{app['name']}")]
        for app in category["apps"]
    ]
    keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_apps")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        texts.get("apps_select", "Please select an app:"),
        reply_markup=reply_markup
    )
    return APP

async def select_app(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the app selection, save to Google Sheets, notify admin, add points, and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    app_name = query.data.split("_")[1]
    category_name = context.user_data["selected_category"]
    profile = context.user_data["user_profile"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"User {user_id} selected app: {app_name} in category: {category_name}")

    apps_data = load_apps()
    category = next((cat for cat in apps_data["categories"] if cat["name"] == category_name), None)
    if not category:
        await query.message.reply_text(
            texts.get("error_message", "Invalid category. Please try again.")
        )
        return ConversationHandler.END

    app = next((app for app in category["apps"] if app["name"] == app_name), None)
    if not app:
        await query.message.reply_text(
            texts.get("error_message", "Invalid app. Please try again.")
        )
        return APP

    app_data = f"{app['name']}: {app['description'][lang]} ({app['link']})"

    try:
        # Save to Google Sheets
        data = [
            user_id,
            profile["first_name"] or "",
            profile["family_name"] or "",
            profile["age"] or "",
            profile["email"] or "",
            profile["field_of_study"] or "",
            profile["country"] or "",
            f"Category: {category['display_name'][lang]}, App: {app_data}",
            "",  # Empty Answer column
            timestamp
        ]
        append_to_sheet("StudentBotQuestions", data)

        # Add points for selecting an app
        db: Session = next(get_db())
        add_points(user_id, 5, db)  # Add 5 points

        # Notify admin
        admin_message = (
            texts.get("apps_admin_notify", "New app selection:\n")
            + f"User ID: {user_id}\n"
            + f"Name: {profile['first_name']} {profile['family_name']}\n"
            + f"Age: {profile['age']}\n"
            + f"Email: {profile['email']}\n"
            + f"Field of Study: {profile['field_of_study']}\n"
            + f"Country: {profile['country']}\n"
            + f"Category: {category['display_name'][lang]}\n"
            + f"App: {app_data}\n"
            + f"Time: {timestamp}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await query.message.reply_text(
            texts.get("apps_submitted", "Thank you for selecting an app! You earned 5 points.\n")
            + f"{app['name']}: {app['description'][lang]}\n"
            + f"Link: {app['link']}"
        )
    except Exception as e:
        logger.error(f"Error saving app selection for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    # Clear data
    context.user_data.pop("selected_category", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

async def cancel_apps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel apps guide and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled apps guide.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "Apps guide cancelled.")
    )
    context.user_data.pop("selected_category", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

# Define ConversationHandler
apps_guide_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("apps", start_apps_guide)],
    states={
        CATEGORY: [CallbackQueryHandler(select_category, pattern="^category_|^cancel_apps$")],
        APP: [CallbackQueryHandler(select_app, pattern="^app_|^cancel_apps$")],
    },
    fallbacks=[CommandHandler("cancel", cancel_apps)],
)

# Define handlers for main.py
handlers = [apps_guide_conv_handler]
