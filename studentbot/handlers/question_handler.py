# بخش: Handlerهای اصلی
# فایل: question_handler.py
# فایل: handlers/question_handler.py
# فایل: handlers/question_handler.py

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
from utils.gsheets import append_to_sheet
from utils.db import get_db, User
from handlers.gamification_handler import add_points
from sqlalchemy.orm import Session
from datetime import datetime
import json

# States for ConversationHandler
QUESTION, CONFIRM = range(2)

from utils.menu_utils import load_texts

async def start_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the question submission process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started question submission.")

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

    await update.message.reply_text(
        texts.get("question_intro", "Please enter your question:")
    )
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's question.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    question = update.message.text.strip()

    if not question or len(question) > 500:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid question (1-500 characters).")
        )
        return QUESTION

    context.user_data["question"] = question
    logger.info(f"User {user_id} entered question: {question}")

    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_question"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_question"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("question_confirm", "Is this your question?") + f"\n\n{question}",
        reply_markup=reply_markup
    )
    return CONFIRM

async def confirm_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the question with profile data to Google Sheets, notify admin, add points, and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    question = context.user_data.get("question")
    profile = context.user_data.get("user_profile")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"User {user_id} confirmed question.")

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
            question,
            "",  # Empty Answer column
            timestamp
        ]
        append_to_sheet("StudentBotQuestions", data)

        # Add points for asking a question
        db: Session = next(get_db())
        add_points(user_id, 10, db)  # Add 10 points

        # Notify admin
        admin_message = (
            texts.get("question_admin_notify", "New question submitted:\n")
            + f"User ID: {user_id}\n"
            + f"Name: {profile['first_name']} {profile['family_name']}\n"
            + f"Age: {profile['age']}\n"
            + f"Email: {profile['email']}\n"
            + f"Field of Study: {profile['field_of_study']}\n"
            + f"Country: {profile['country']}\n"
            + f"Question: {question}\n"
            + f"Time: {timestamp}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await query.message.reply_text(
            texts.get("question_submitted", "Your question has been submitted successfully! You earned 10 points.")
        )
    except Exception as e:
        logger.error(f"Error saving question for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    # Clear question data
    context.user_data.pop("question", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

async def cancel_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel question submission and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled question submission.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "Question submission cancelled.")
    )
    context.user_data.pop("question", None)
    context.user_data.pop("user_profile", None)
    return ConversationHandler.END

# Define ConversationHandler
question_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", start_question)],
    states={
        QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)],
        CONFIRM: [
            CallbackQueryHandler(confirm_question, pattern="^confirm_question$"),
            CallbackQueryHandler(cancel_question, pattern="^cancel_question$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_question)],
)

# Define handlers for main.py
handlers = [question_conv_handler]
