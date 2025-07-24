from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
import json
import os

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_files():
    with open('studentbot/files.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def show_file_menu(update: Update, context: CallbackContext):
    """Shows the file menu."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    files = load_files()

    keyboard = []
    for pdf_file in files.get("pdfs", []):
        keyboard.append([InlineKeyboardButton(pdf_file, callback_data=f"file_pdf_{pdf_file}")])
    for video_file in files.get("videos", []):
        keyboard.append([InlineKeyboardButton(video_file, callback_data=f"file_video_{video_file}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(texts.get("file_menu_prompt", "Please select a file:"), reply_markup=reply_markup)

async def send_file(update: Update, context: CallbackContext):
    """Sends the selected file."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    file_type, file_name = query.data.split('_')[1:]
    file_path = f"assets/{file_type}s/{file_name}"

    try:
        with open(file_path, "rb") as file:
            if file_type == 'pdf':
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file)
            elif file_type == 'video':
                await context.bot.send_video(chat_id=update.effective_chat.id, video=file)
    except FileNotFoundError:
        await query.message.reply_text(texts.get("file_not_found", "File not found."))

file_menu_handler = CallbackQueryHandler(show_file_menu, pattern='^file$')
file_sender_handler = CallbackQueryHandler(send_file, pattern='^file_')
