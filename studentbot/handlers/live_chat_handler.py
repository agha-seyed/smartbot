from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters
from config import ADMIN_CHAT_ID, logger
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def start_chat(update: Update, context: CallbackContext):
    """Starts a live chat session."""
    logger.info(f"User {update.effective_user.id} started a live chat.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    context.user_data['in_chat'] = True
    await query.message.reply_text(texts["chat_started"])
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"User {update.effective_user.id} started a chat.")

async def end_chat(update: Update, context: CallbackContext):
    logger.info(f"User {update.effective_user.id} ended a live chat.")
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    context.user_data['in_chat'] = False
    await update.message.reply_text(texts["chat_ended"])
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"User {update.effective_user.id} ended the chat.")

async def forward_to_admin(update: Update, context: CallbackContext):
    if context.user_data.get('in_chat'):
        await context.bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)

async def forward_to_user(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == ADMIN_CHAT_ID and update.message.reply_to_message and update.message.reply_to_message.forward_from:
        user_id = update.message.reply_to_message.forward_from.id
        await context.bot.send_message(chat_id=user_id, text=update.message.text)

from telegram.ext import CallbackQueryHandler

start_chat_handler = CallbackQueryHandler(start_chat, pattern='^live_chat$')
end_chat_handler = CommandHandler("endchat", end_chat)
user_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY, forward_to_admin)
admin_message_handler = MessageHandler(filters.REPLY, forward_to_user)
