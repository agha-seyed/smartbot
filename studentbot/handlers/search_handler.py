from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from fuzzywuzzy import process
from config import logger
import json

def load_knowledge_base():
    with open('lang/knowledge_base.json', 'r', encoding='utf-8') as f:
        return json.load(f)

knowledge_base = load_knowledge_base()

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Stages
SEARCHING = range(1)

async def start_search(update: Update, context: CallbackContext):
    """Starts the search conversation."""
    logger.info(f"User {update.effective_user.id} started a search.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await query.message.reply_text(texts.get("search_prompt", "What are you looking for?"))
    return SEARCHING

async def search(update: Update, context: CallbackContext):
    user_query = update.message.text
    logger.info(f"User {update.effective_user.id} searched for: {user_query}")
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    questions = list(knowledge_base[lang].keys())
    best_match = process.extractOne(user_query, questions)

    if best_match and best_match[1] > 80:  # Confidence threshold
        answer = knowledge_base[lang][best_match[0]]
        logger.info(f"Found match for '{user_query}': {best_match[0]}")
        await update.message.reply_text(answer)
    else:
        logger.info(f"No match found for '{user_query}'")
        await update.message.reply_text(texts.get("search_no_result", "Sorry, I couldn't find an answer to your question."))

    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(texts["conversation_cancelled"])
    return ConversationHandler.END

search_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_search, pattern='^search$')],
    states={
        SEARCHING: [MessageHandler(filters.TEXT & ~filters.COMMAND, search)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
