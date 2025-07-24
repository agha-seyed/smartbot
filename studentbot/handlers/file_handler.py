from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def send_pdf(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    pdf_id = context.args[0] if context.args else None
    if not pdf_id:
        await update.message.reply_text(texts["pdf_id_missing"])
        return

    try:
        with open(f"assets/pdfs/{pdf_id}.pdf", "rb") as pdf_file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=pdf_file)
    except FileNotFoundError:
        await update.message.reply_text(texts["pdf_not_found"])

async def send_video(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    video_id = context.args[0] if context.args else None
    if not video_id:
        await update.message.reply_text(texts["video_id_missing"])
        return

    try:
        with open(f"assets/videos/{video_id}.mp4", "rb") as video_file:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video_file)
    except FileNotFoundError:
        await update.message.reply_text(texts["video_not_found"])


pdf_handler = CommandHandler("pdf", send_pdf)
video_handler = CommandHandler("video", send_video)
