from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters
from utils.gsheets import save_to_gsheets
from config import ADMIN_CHAT_ID, QUESTIONS_SHEET_NAME
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Stages
QUESTION = range(1)

async def start_question(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(texts["question_intro"])
    return QUESTION

async def get_question(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    question_data = {
        "user_id": update.effective_user.id,
        "question": update.message.text
    }

    save_to_gsheets(question_data, sheet_name=QUESTIONS_SHEET_NAME)

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"New question from user {update.effective_user.id}:\n\n{update.message.text}"
    )

    await update.message.reply_text(texts["question_submitted"])
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(texts["conversation_cancelled"])
    return ConversationHandler.END

question_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("question", start_question)],
    states={
        QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
