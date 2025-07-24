from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
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

    keyboard = [
        [InlineKeyboardButton(texts.get("menu_scholarships", "-"), callback_data='menu_scholarships')],
        [InlineKeyboardButton(texts.get("menu_migration", "-"), callback_data='menu_migration')],
        [InlineKeyboardButton(texts.get("menu_housing", "-"), callback_data='menu_housing')],
        [InlineKeyboardButton(texts.get("menu_student_life", "-"), callback_data='menu_student_life')],
        [InlineKeyboardButton(texts.get("menu_universities", "-"), callback_data='menu_universities')],
        [InlineKeyboardButton(texts.get("menu_isee_calculator", "-"), callback_data='isee_calculator')],
        [InlineKeyboardButton(texts.get("menu_weather", "-"), callback_data='weather')],
        [InlineKeyboardButton(texts.get("menu_ask_question", "-"), callback_data='ask_question')],
        [InlineKeyboardButton(texts.get("menu_tools", "-"), callback_data='menu_tools')],
        [InlineKeyboardButton("📲 اپ‌ها و راهنمای ورود", callback_data='apps_entry_guide')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=texts['welcome'],
        reply_markup=reply_markup
    )

async def placeholder_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("این بخش در حال ساخت است.")

start_handler = CommandHandler("start", start)
lang_handler = CallbackQueryHandler(language_select, pattern='^lang_')
placeholder_handler = CallbackQueryHandler(placeholder_handler, pattern='^menu_')
