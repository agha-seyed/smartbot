# بخش: قابلیت‌های اضافی
# فایل: location_handler.py

# فایل: handlers/location_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from studentbot.config import logger, ADMIN_CHAT_ID
from studentbot.utils.gsheets import append_to_sheet
from studentbot.utils.db import get_db, User
from studentbot.handlers.gamification_handler import add_points
from sqlalchemy.orm import Session
from datetime import datetime
import json

# States for ConversationHandler
LOCATION, CONFIRM = range(2)

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

async def start_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the location submission process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started location submission.")

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

    # Create a button to request location
    keyboard = [
        [KeyboardButton(texts.get("send_location", "Send My Location"), request_location=True)],
        [KeyboardButton(texts.get("enter_city", "Enter City Name"))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        texts.get("location_intro", "Please share your location by clicking the button below or enter your city name manually:"),
        reply_markup=reply_markup
    )
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's location or city name.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    profile = context.user_data.get("user_profile")

    # Handle location
    if update.message.location:
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        location_data = f"Latitude: {latitude}, Longitude: {longitude}"
        logger.info(f"User {user_id} shared location: {location_data}")
    else:
        # Handle city name
        city_name = update.message.text.strip()
        if not city_name or len(city_name) > 100:
            await update.message.reply_text(
                texts.get("error_message", "Please enter a valid city name (1-100 characters).")
            )
            return LOCATION
        location_data = f"City: {city_name}"
        logger.info(f"User {user_id} entered city: {city_name}")

    context.user_data["location_data"] = location_data

    # Show confirmation
    location_summary = (
        f"{texts.get('profile_name', 'Name')}: {profile['first_name']}\n"
        f"{texts.get('profile_family_name', 'Family Name')}: {profile['family_name']}\n"
        f"{texts.get('profile_age', 'Age')}: {profile['age']}\n"
        f"{texts.get('profile_email', 'Email')}: {profile['email']}\n"
        f"{texts.get('profile_field_of_study', 'Field of Study')}: {profile['field_of_study']}\n"
        f"{texts.get('profile_country', 'Country')}: {profile['country']}\n"
        f"{texts.get('location_data', 'Location')}: {location_data}"
    )
    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_location"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_location"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("location_confirm", "Please confirm your location:") + "\n\n" + location_summary,
        reply_markup=reply_markup
    )
    return CONFIRM

async def confirm_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the location data to Google Sheets, notify admin, add points, and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = context.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    location_data = context.user_data["location_data"]
    profile = context.user_data.get("user_profile")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"User {user_id} confirmed location: {location_data}")

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
            location_data,
            "",  # Empty Answer column
            timestamp
        ]
        append_to_sheet("StudentBotQuestions", data)

        # Add points for sharing location
        db: Session = next(get_db())
        add_points(user_id, 10, db)  # Add 10 points

        # Notify admin
        admin_message = (
            texts.get("location_admin_notify", "New location submitted:\n")
            + f"User ID: {user_id}\n"
            + f"Name: {profile['first_name']} {profile['family_name']}\n"
            + f"Age: {profile['age']}\n"
            + f"Email: {profile['email']}\n"
            + f"Field of Study: {profile['field_of_study']}\n"
            + f"Country: {profile['country']}\n"
            + f"Location: {location_data}\n"
            + f"Time: {timestamp}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await query.message.reply_text(
            texts.get("location_submitted", "Your location has been submitted successfully! You earned 10 points.")
        )
    except Exception as e:
        logger.error(f"Error saving location for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    # Clear location data
    context.user_data.pop("location_data", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

async def cancel_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel location submission and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = context.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled location submission.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "Location submission cancelled.")
    )
    context.user_data.pop("location_data", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

# Define ConversationHandler
location_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("location", start_location)],
    states={
        LOCATION: [
            MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), get_location)
        ],
        CONFIRM: [
            CallbackQueryHandler(confirm_location, pattern="^confirm_location$"),
            CallbackQueryHandler(cancel_location, pattern="^cancel_location$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_location)],
)

# Define handlers for main.py
handlers = [location_conv_handler]
