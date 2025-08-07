# بخش: جریان اصلی ربات
# فایل: profile_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from studentbot.config import logger
from studentbot.utils.db import get_db, User
from sqlalchemy.orm import Session
import json
import re

# States for ConversationHandler
NAME, FAMILY_NAME, AGE, EMAIL, FIELD_OF_STUDY, COUNTRY, CONFIRM = range(7)

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

async def start_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the profile creation process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started profile creation.")

    # Check if profile already exists
    db: Session = next(get_db())
    existing_user = db.query(User).filter_by(user_id=user_id).first()
    if existing_user:
        await update.message.reply_text(
            texts.get("profile_complete", "You already have a profile.")
        )
        return ConversationHandler.END

    await update.message.reply_text(
        texts.get("profile_creation_intro", "Let's create your profile!") + "\n" +
        texts.get("profile_name", "What's your first name?")
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's first name.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    name = update.message.text.strip()

    if not name or len(name) > 50:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid first name (1-50 characters).")
        )
        return NAME

    context.user_data["profile_name"] = name
    logger.info(f"User {user_id} entered name: {name}")
    await update.message.reply_text(
        texts.get("profile_family_name", "What's your family name?")
    )
    return FAMILY_NAME

async def get_family_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's family name.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    family_name = update.message.text.strip()

    if not family_name or len(family_name) > 50:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid family name (1-50 characters).")
        )
        return FAMILY_NAME

    context.user_data["profile_family_name"] = family_name
    logger.info(f"User {user_id} entered family name: {family_name}")
    await update.message.reply_text(
        texts.get("profile_age", "How old are you?")
    )
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's age.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    age_text = update.message.text.strip()

    try:
        age = int(age_text)
        if age < 16 or age > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid age (16-100).")
        )
        return AGE

    context.user_data["profile_age"] = age
    logger.info(f"User {user_id} entered age: {age}")
    await update.message.reply_text(
        texts.get("profile_email", "What's your email address?")
    )
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's email.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    email = update.message.text.strip()

    # Basic email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid email address.")
        )
        return EMAIL

    context.user_data["profile_email"] = email
    logger.info(f"User {user_id} entered email: {email}")
    await update.message.reply_text(
        texts.get("profile_field_of_study", "What's your field of study?")
    )
    return FIELD_OF_STUDY

async def get_field_of_study(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's field of study.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    field_of_study = update.message.text.strip()

    if not field_of_study or len(field_of_study) > 100:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid field of study (1-100 characters).")
        )
        return FIELD_OF_STUDY

    context.user_data["profile_field_of_study"] = field_of_study
    logger.info(f"User {user_id} entered field of study: {field_of_study}")
    await update.message.reply_text(
        texts.get("profile_country", "What's your country?")
    )
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's country.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    country = update.message.text.strip()

    if not country or len(country) > 50:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid country (1-50 characters).")
        )
        return COUNTRY

    context.user_data["profile_country"] = country
    logger.info(f"User {user_id} entered country: {country}")

    # Show confirmation message
    profile_summary = (
        f"{texts.get('profile_name', 'Name')}: {context.user_data['profile_name']}\n"
        f"{texts.get('profile_family_name', 'Family Name')}: {context.user_data['profile_family_name']}\n"
        f"{texts.get('profile_age', 'Age')}: {context.user_data['profile_age']}\n"
        f"{texts.get('profile_email', 'Email')}: {context.user_data['profile_email']}\n"
        f"{texts.get('profile_field_of_study', 'Field of Study')}: {context.user_data['profile_field_of_study']}\n"
        f"{texts.get('profile_country', 'Country')}: {context.user_data['profile_country']}"
    )
    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_profile"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_profile"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("profile_complete", "Please confirm your profile:") + "\n\n" + profile_summary,
        reply_markup=reply_markup
    )
    return CONFIRM

from studentbot.services.profile_service import create_profile, delete_profile

async def confirm_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the profile to the database and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} confirmed profile.")

    try:
        create_profile(user_id, context.user_data)
        logger.info(f"Profile saved for user {user_id}")
        await query.message.reply_text(
            texts.get("profile_complete", "Your profile has been created successfully!")
        )
    except Exception as e:
        logger.error(f"Error saving profile for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    # Clear profile data
    for key in ["profile_name", "profile_family_name", "profile_age", "profile_email", "profile_field_of_study", "profile_country"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

async def cancel_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel profile creation and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled profile creation.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "Profile creation cancelled.")
    )

    # Clear profile data
    for key in ["profile_name", "profile_family_name", "profile_age", "profile_email", "profile_field_of_study", "profile_country"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

# States for delete profile conversation
CONFIRM_DELETE = range(1)

async def delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the profile deletion process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started profile deletion.")

    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_delete"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_delete"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("profile_delete_confirm", "Are you sure you want to delete your profile? This action cannot be undone."),
        reply_markup=reply_markup
    )
    return CONFIRM_DELETE

async def confirm_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Delete the user's profile from the database and Google Sheets.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} confirmed profile deletion.")

    try:
        delete_profile(user_id)
        logger.info(f"Profile deleted for user {user_id}")
        await query.message.reply_text(
            texts.get("profile_deleted", "Your profile has been deleted successfully.")
        )
    except Exception as e:
        logger.error(f"Error deleting profile for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    return ConversationHandler.END

async def cancel_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel profile deletion.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled profile deletion.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "Profile deletion cancelled.")
    )
    return ConversationHandler.END

# Define ConversationHandlers
profile_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("profile", start_profile)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        FAMILY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_family_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        FIELD_OF_STUDY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_field_of_study)],
        COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
        CONFIRM: [
            CallbackQueryHandler(confirm_profile, pattern="^confirm_profile$"),
            CallbackQueryHandler(cancel_profile, pattern="^cancel_profile$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_profile)],
)

delete_profile_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("delete_profile", delete_profile)],
    states={
        CONFIRM_DELETE: [
            CallbackQueryHandler(confirm_delete_profile, pattern="^confirm_delete$"),
            CallbackQueryHandler(cancel_delete_profile, pattern="^cancel_delete$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_delete_profile)],
)

# Define handlers for main.py
handlers = [profile_conv_handler, delete_profile_conv_handler]
