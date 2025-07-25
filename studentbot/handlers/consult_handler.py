# بخش: Handlerهای اصلی
# فایل: consult_handler.py

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
from config import logger, ADMIN_CHAT_ID
from utils.redis_utils import cache_session, get_session
from utils.gsheets import append_to_sheet
from datetime import datetime
import json

# States for ConversationHandler
FIELD, DETAILS, CONFIRM = range(3)

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

async def start_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the consultation request process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started consultation request.")

    keyboard = [
        [InlineKeyboardButton(texts.get("consult_migration", "Migration"), callback_data="consult_migration")],
        [InlineKeyboardButton(texts.get("consult_scholarship", "Scholarship"), callback_data="consult_scholarship")],
        [InlineKeyboardButton(texts.get("consult_residence", "Residence"), callback_data="consult_residence")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("consult_intro", "Please select a consultation field:"),
        reply_markup=reply_markup
    )
    return FIELD

async def select_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the consultation field selection.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    field = query.data.split("_")[1]
    context.user_data["consult_field"] = field
    logger.info(f"User {user_id} selected consultation field: {field}")

    await query.message.reply_text(
        texts.get("consult_details", "Please provide details for your consultation request:")
    )
    return DETAILS

async def get_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the consultation details.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    details = update.message.text.strip()

    if not details or len(details) > 1000:
        await update.message.reply_text(
            texts.get("error_message", "Please enter valid details (1-1000 characters).")
        )
        return DETAILS

    context.user_data["consult_details"] = details
    logger.info(f"User {user_id} provided consultation details.")

    # Show confirmation message
    consult_summary = (
        f"{texts.get('consult_field', 'Field')}: {context.user_data['consult_field']}\n"
        f"{texts.get('consult_details', 'Details')}: {details}"
    )
    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_consult"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_consult"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("consult_confirm", "Please confirm your consultation request:") + "\n\n" + consult_summary,
        reply_markup=reply_markup
    )
    return CONFIRM

async def confirm_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the consultation request to Google Sheets and Redis, notify admin, and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    field = context.user_data.get("consult_field")
    details = context.user_data.get("consult_details")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"User {user_id} confirmed consultation request.")

    try:
        # Save to Google Sheets
        data = [user_id, field, details, timestamp]
        append_to_sheet("StudentBotQuestions", data)

        # Save session to Redis
        session_data = {"field": field, "details": details, "timestamp": timestamp}
        cache_session(user_id, session_data)

        # Notify admin
        admin_message = (
            texts.get("consult_admin_notify", "New consultation request:\n")
            + f"User ID: {user_id}\n"
            + f"Field: {field}\n"
            + f"Details: {details}\n"
            + f"Time: {timestamp}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await query.message.reply_text(
            texts.get("consult_submitted", "Your consultation request has been submitted successfully!")
        )
    except Exception as e:
        logger.error(f"Error saving consultation for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    # Clear consultation data
    for key in ["consult_field", "consult_details"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

async def cancel_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel consultation request and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled consultation request.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "Consultation request cancelled.")
    )

    # Clear consultation data
    for key in ["consult_field", "consult_details"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

# Define ConversationHandler
consult_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("consult", start_consultation)],
    states={
        FIELD: [CallbackQueryHandler(select_field, pattern="^consult_")],
        DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_details)],
        CONFIRM: [
            CallbackQueryHandler(confirm_consultation, pattern="^confirm_consult$"),
            CallbackQueryHandler(cancel_consultation, pattern="^cancel_consult$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_consultation)],
)

# Define handlers for main.py
handlers = [consult_conv_handler]
