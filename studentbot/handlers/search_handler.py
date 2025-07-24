from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters
from fuzzywuzzy import process
import json

def load_knowledge_base():
    with open('lang/knowledge_base.json', 'r', encoding='utf-8') as f:
        return json.load(f)

knowledge_base = load_knowledge_base()

async def search(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    user_query = update.message.text

    questions = list(knowledge_base[lang].keys())
    best_match = process.extractOne(user_query, questions)

    if best_match and best_match[1] > 80:  # Confidence threshold
        answer = knowledge_base[lang][best_match[0]]
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("متاسفانه جوابی برای سوال شما پیدا نکردم.")

search_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, search)
