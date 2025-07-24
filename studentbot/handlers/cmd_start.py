from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("فارسی", callback_data='lang_fa')],
        [InlineKeyboardButton("English", callback_data='lang_en')],
        [InlineKeyboardButton("Italiano", callback_data='lang_it')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفا زبان خود را انتخاب کنید / Please select your language / Seleziona la tua lingua:", reply_markup=reply_markup)

async def language_select(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split('_')[1]
    context.user_data['lang'] = lang_code
    texts = load_texts(lang_code)
    await query.edit_message_text(text=texts['welcome'])
    # Here you would typically show the main menu
    # For now, we just show a welcome message
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Main menu would be here.")

lang_handler = CallbackQueryHandler(language_select, pattern='^lang_')
