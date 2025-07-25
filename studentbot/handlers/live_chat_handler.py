# بخش: قابلیت‌های اضافی
# فایل: live_chat_handler.py

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
from utils.db import get_db, User
from utils.gamification import add_points
from sqlalchemy.orm import Session
from datetime import datetime
import json

# States for ConversationHandler
CHAT = 0

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

async def start_live_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the live chat session.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started live chat.")

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

    # Check if admin is available (placeholder for future admin status check)
    session_data = {"status": "active", "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    cache_session(user_id, session_data)

    keyboard = [
        [InlineKeyboardButton(texts.get("end_chat", "End Chat"), callback_data="end_chat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("live_chat_intro", "You are now in live chat mode. Send your message, and the admin will respond soon. Use /cancel or the button below to end the chat."),
        reply_markup=reply_markup
    )
    return CHAT

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle messages sent by the user during live chat.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    message_text = update.message.text.strip()
    profile = context.user_data.get("user_profile")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"User {user_id} sent live chat message: {message_text}")

    if not message_text or len(message_text) > 1000:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid message (1-1000 characters).")
        )
        return CHAT

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
            message_text,
            "",  # Empty Answer column
            timestamp
        ]
        append_to_sheet("StudentBotQuestions", data)

        # Add points for chat message
        db: Session = next(get_db())
        add_points(user_id, 5, db)  # Add 5 points for each message

        # Forward message to admin
        admin_message = (
            texts.get("live_chat_admin_notify", "New live chat message:\n")
            + f"User ID: {user_id}\n"
            + f"Name: {profile['first_name']} {profile['family_name']}\n"
            + f"Age: {profile['age']}\n"
            + f"Email: {profile['email']}\n"
            + f"Field of Study: {profile['field_of_study']}\n"
            + f"Country: {profile['country']}\n"
            + f"Message: {message_text}\n"
            + f"Time: {timestamp}"
        )
        await context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=user_id,
            message_id=update.message.message_id
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await update.message.reply_text(
            texts.get("live_chat_message_sent", "Your message has been sent to the admin. You earned 5 points. Please wait for a response.")
        )
    except Exception as e:
        logger.error(f"Error handling live chat message for user {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    return CHAT

async def handle_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle admin responses to live chat messages (if replied to a forwarded message).
    """
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        return  # Only admin can trigger this handler

    if not update.message.reply_to_message or not update.message.reply_to_message.forward_from:
        return  # Ensure it's a reply to a forwarded message

    target_user_id = update.message.reply_to_message.forward_from.id
    lang = context.user_data.get("lang", "fa")  # Fallback language for admin
    texts = load_texts(lang)
    response_text = update.message.text.strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Admin {user_id} responded to user {target_user_id}: {response_text}")

    try:
        # Check if user is still in live chat session
        session = get_session(target_user_id)
        if not session or session.get("status") != "active":
            await update.message.reply_text(
                texts.get("live_chat_inactive", "The user is no longer in live chat mode.")
            )
            return

        # Send response to user
        await context.bot.send_message(
            chat_id=target_user_id,
            text=texts.get("live_chat_admin_response", "Admin response: {response}").format(response=response_text)
        )

        # Update Google Sheets with admin response
        db: Session = next(get_db())
        user = db.query(User).filter_by(user_id=target_user_id).first()
        if user:
            data = [
                target_user_id,
                user.first_name or "",
                user.family_name or "",
                user.age or "",
                user.email or "",
                user.field_of_study or "",
                user.country or "",
                "",  # Empty Question column
                response_text,  # Admin response
                timestamp
            ]
            append_to_sheet("StudentBotQuestions", data)
    except Exception as e:
        logger.error(f"Error handling admin response for user {target_user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred while sending the response.")
        )

async def end_live_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    End the live chat session.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} ended live chat.")

    # Clear session from Redis
    session_data = {"status": "inactive"}
    cache_session(user_id, session_data)

    await query.message.reply_text(
        texts.get("live_chat_ended", "Live chat session ended.")
    )

    # Clear user data
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

async def cancel_live_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel live chat and end the conversation.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled live chat.")

    # Clear session from Redis
    session_data = {"status": "inactive"}
    cache_session(user_id, session_data)

    await update.message.reply_text(
        texts.get("conversation_cancelled", "Live chat cancelled.")
    )

    # Clear user data
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

# Define ConversationHandler
live_chat_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("livechat", start_live_chat)],
    states={
        CHAT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat_message),
            CallbackQueryHandler(end_live_chat, pattern="^end_chat$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_live_chat)],
)

# Define handlers for main.py
handlers = [
    live_chat_conv_handler,
    MessageHandler(filters.REPLY & filters.User(user_id=ADMIN_CHAT_ID), handle_admin_response),
]