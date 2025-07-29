# بخش: قابلیت‌های اضافی
# فایل: feedback_handler.py

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
from studentbot.config import logger, ADMIN_CHAT_ID
from studentbot.utils.gsheets import append_to_sheet
from studentbot.utils.db import get_db, User
from studentbot.handlers.gamification_handler import add_points
from sqlalchemy.orm import Session
from datetime import datetime
import json

# States for ConversationHandler
FEEDBACK_TYPE, FEEDBACK_TEXT, FEEDBACK_RATING, CONFIRM = range(4)

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

async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the feedback submission process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started feedback submission.")

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

    keyboard = [
        [InlineKeyboardButton(texts.get("feedback_text", "Write Feedback"), callback_data="feedback_text")],
        [InlineKeyboardButton(texts.get("feedback_rating", "Rate (1-5)"), callback_data="feedback_rating")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("feedback_intro", "Would you like to write feedback or rate the bot (1-5)?"),
        reply_markup=reply_markup
    )
    return FEEDBACK_TYPE

async def select_feedback_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the feedback type selection (text or rating).
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    feedback_type = query.data
    context.user_data["feedback_type"] = feedback_type
    logger.info(f"User {user_id} selected feedback type: {feedback_type}")

    if feedback_type == "feedback_text":
        await query.message.reply_text(
            texts.get("feedback_text_prompt", "Please write your feedback:")
        )
        return FEEDBACK_TEXT
    else:
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data="rating_1"),
                InlineKeyboardButton("2", callback_data="rating_2"),
                InlineKeyboardButton("3", callback_data="rating_3"),
                InlineKeyboardButton("4", callback_data="rating_4"),
                InlineKeyboardButton("5", callback_data="rating_5"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            texts.get("feedback_rating_prompt", "Please select a rating (1-5):"),
            reply_markup=reply_markup
        )
        return FEEDBACK_RATING

async def get_feedback_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's feedback text.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    feedback_text = update.message.text.strip()

    if not feedback_text or len(feedback_text) > 1000:
        await update.message.reply_text(
            texts.get("error_message", "Please enter valid feedback (1-1000 characters).")
        )
        return FEEDBACK_TEXT

    context.user_data["feedback_data"] = feedback_text
    logger.info(f"User {user_id} provided feedback text: {feedback_text}")

    # Show confirmation
    profile = context.user_data["user_profile"]
    feedback_summary = (
        f"{texts.get('profile_name', 'Name')}: {profile['first_name']}\n"
        f"{texts.get('profile_family_name', 'Family Name')}: {profile['family_name']}\n"
        f"{texts.get('profile_age', 'Age')}: {profile['age']}\n"
        f"{texts.get('profile_email', 'Email')}: {profile['email']}\n"
        f"{texts.get('profile_field_of_study', 'Field of Study')}: {profile['field_of_study']}\n"
        f"{texts.get('profile_country', 'Country')}: {profile['country']}\n"
        f"{texts.get('feedback_data', 'Feedback')}: {feedback_text}"
    )
    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_feedback"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_feedback"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("feedback_confirm", "Please confirm your feedback:") + "\n\n" + feedback_summary,
        reply_markup=reply_markup
    )
    return CONFIRM

async def get_feedback_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's rating selection.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    rating = int(query.data.split("_")[1])
    context.user_data["feedback_data"] = f"Rating: {rating}/5"
    logger.info(f"User {user_id} provided rating: {rating}")

    # Show confirmation
    profile = context.user_data["user_profile"]
    feedback_summary = (
        f"{texts.get('profile_name', 'Name')}: {profile['first_name']}\n"
        f"{texts.get('profile_family_name', 'Family Name')}: {profile['family_name']}\n"
        f"{texts.get('profile_age', 'Age')}: {profile['age']}\n"
        f"{texts.get('profile_email', 'Email')}: {profile['email']}\n"
        f"{texts.get('profile_field_of_study', 'Field of Study')}: {profile['field_of_study']}\n"
        f"{texts.get('profile_country', 'Country')}: {profile['country']}\n"
        f"{texts.get('feedback_data', 'Feedback')}: {texts.get('feedback_rating', 'Rating')}: {rating}/5"
    )
    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_feedback"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_feedback"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        texts.get("feedback_confirm", "Please confirm your feedback:") + "\n\n" + feedback_summary,
        reply_markup=reply_markup
    )
    return CONFIRM

async def confirm_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the feedback to Google Sheets, notify admin, add points, and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    feedback_data = context.user_data["feedback_data"]
    profile = context.user_data["user_profile"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"User {user_id} confirmed feedback: {feedback_data}")

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
            feedback_data,
            "",  # Empty Answer column
            timestamp
        ]
        append_to_sheet("StudentBotQuestions", data)

        # Add points for feedback
        db: Session = next(get_db())
        add_points(user_id, 5, db)  # Add 5 points

        # Notify admin
        admin_message = (
            texts.get("feedback_admin_notify", "New feedback submitted:\n")
            + f"User ID: {user_id}\n"
            + f"Name: {profile['first_name']} {profile['family_name']}\n"
            + f"Age: {profile['age']}\n"
            + f"Email: {profile['email']}\n"
            + f"Field of Study: {profile['field_of_study']}\n"
            + f"Country: {profile['country']}\n"
            + f"Feedback: {feedback_data}\n"
            + f"Time: {timestamp}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await query.message.reply_text(
            texts.get("feedback_submitted", "Your feedback has been submitted successfully! You earned 5 points.")
        )
    except Exception as e:
        logger.error(f"Error saving feedback for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    # Clear feedback data
    context.user_data.pop("feedback_type", None)
    context.user_data.pop("feedback_data", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel feedback submission and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled feedback submission.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "Feedback submission cancelled.")
    )
    context.user_data.pop("feedback_type", None)
    context.user_data.pop("feedback_data", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

# Define ConversationHandler
feedback_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("feedback", start_feedback)],
    states={
        FEEDBACK_TYPE: [
            CallbackQueryHandler(select_feedback_type, pattern="^feedback_")
        ],
        FEEDBACK_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_feedback_text)
        ],
        FEEDBACK_RATING: [
            CallbackQueryHandler(get_feedback_rating, pattern="^rating_")
        ],
        CONFIRM: [
            CallbackQueryHandler(confirm_feedback, pattern="^confirm_feedback$"),
            CallbackQueryHandler(cancel_feedback, pattern="^cancel_feedback$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_feedback)],
)

# Define handlers for main.py
handlers = [feedback_conv_handler]
