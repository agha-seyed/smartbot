from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,  # اضافه کردن CallbackQueryHandler
)
from utils.gsheets import save_to_gsheets
from config import ADMIN_CHAT_ID, QUESTIONS_SHEET_NAME, logger
from utils.text_formatter import sanitize_markdown
import json

# مراحل مکالمه
QUESTION = range(1)

def load_texts(lang):
    """Load language-specific texts from JSON files."""
    try:
        with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Language file lang/{lang}.json not found.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in lang/{lang}.json.")
        raise

async def start_question(update: Update, context: CallbackContext):
    """Starts the question submission conversation."""
    logger.info(f"User {update.effective_user.id} started a question.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(sanitize_markdown(texts["question_intro"]))
        return QUESTION
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def get_question(update: Update, context: CallbackContext):
    """Receives the user's question and saves it to Google Sheets."""
    logger.info(f"User {update.effective_user.id} submitted a question.")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
    except Exception as e:
        logger.error(f"Error loading texts for {lang}: {e}")
        await update.message.reply_text("Error: Language data is unavailable.")
        return ConversationHandler.END

    question_data = {
        "user_id": update.effective_user.id,
        "question": update.message.text
    }

    try:
        save_to_gsheets(question_data, sheet_name=QUESTIONS_SHEET_NAME)
        logger.info(f"Question from user {update.effective_user.id} saved to Google Sheets.")
    except Exception as e:
        logger.error(f"Could not save question from user {update.effective_user.id} to Google Sheets: {e}")
        await update.message.reply_text(sanitize_markdown(texts.get("error_message", "An error occurred.")))
        return ConversationHandler.END

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"New question from user {update.effective_user.id}:\n\n{update.message.text}"
        )
        logger.info(f"Admin notified for new question from user {update.effective_user.id}.")
    except Exception as e:
        logger.error(f"Could not notify admin for new question from user {update.effective_user.id}: {e}")

    await update.message.reply_text(sanitize_markdown(texts["question_submitted"]))
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    """Cancels the question submission conversation."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await update.message.reply_text(sanitize_markdown(texts["conversation_cancelled"]))
    except Exception as e:
        logger.error(f"Error loading texts for {lang}: {e}")
        await update.message.reply_text("Operation cancelled due to an error.")
    return ConversationHandler.END

question_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_question, pattern='^question$')],
    states={
        QUESTION: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_question)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False
)
