from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters
from utils.db import save_feedback
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def get_feedback(update: Update, context: CallbackContext):
    """Saves the user's feedback."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    feedback_data = {
        "user_id": update.effective_user.id,
        "feedback": update.message.text
    }
    save_feedback(feedback_data)
    await update.message.reply_text(texts.get("feedback_thanks", "Thank you for your feedback!"))
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    """Cancels the conversation."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(texts.get("conversation_cancelled", "Operation cancelled."))
    return ConversationHandler.END

feedback_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, get_feedback)],
    states={},
    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    map_to_parent={
        ConversationHandler.END: ConversationHandler.END,
    },
)
