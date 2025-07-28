# بخش: Handlerهای اصلی
# فایل: file_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from config import logger
from utils.google_drive import upload_file_to_drive
import json
import os

# States for ConversationHandler
FILE, CONFIRM = range(2)

def load_texts(lang: str) -> dict:
    """
    Load language-specific texts from JSON files.
    """
    try:
        with open(f"lang/{lang}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Language file lang/{lang}.json not found.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in lang/{lang}.json.")
        return {}

async def start_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the file upload process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started file upload.")

    await update.message.reply_text(
        texts.get("file_upload_prompt", "Please send the file you want to upload.")
    )
    return FILE

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the received file.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    try:
        file = await update.message.document.get_file()
        file_path = f"temp/{file.file_id}"
        await file.download_to_drive(file_path)

        context.user_data["file_path"] = file_path
        context.user_data["file_name"] = update.message.document.file_name

        keyboard = [
            [
                InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_upload"),
                InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_upload"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            texts.get("file_upload_confirm", "Are you sure you want to upload this file?"),
            reply_markup=reply_markup
        )
        return CONFIRM
    except Exception as e:
        logger.error(f"Error handling file for user {user_id}: {e}")
        await update.message.reply_text(texts.get("error_message", "An error occurred."))
        return ConversationHandler.END

async def confirm_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Upload the file to Google Drive and send the link to the user.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    try:
        file_path = context.user_data["file_path"]
        file_name = context.user_data["file_name"]

        file_link = upload_file_to_drive(file_path, file_name)

        await query.message.reply_text(
            texts.get("file_upload_success", "File uploaded successfully! You can access it here: {file_link}").format(file_link=file_link)
        )

        os.remove(file_path) # Clean up the temp file

    except Exception as e:
        logger.error(f"Error uploading file for user {user_id}: {e}")
        await query.message.reply_text(texts.get("error_message", "An error occurred during upload."))

    for key in ["file_path", "file_name"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel the file upload.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    try:
        file_path = context.user_data.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        await query.message.reply_text(
            texts.get("conversation_cancelled", "File upload cancelled.")
        )
    except Exception as e:
        logger.error(f"Error cancelling upload for user {user_id}: {e}")
        await query.message.reply_text(texts.get("error_message", "An error occurred."))

    for key in ["file_path", "file_name"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

# Define ConversationHandler
file_upload_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("upload", start_file_upload)],
    states={
        FILE: [MessageHandler(filters.Document.ALL, get_file)],
        CONFIRM: [
            CallbackQueryHandler(confirm_upload, pattern="^confirm_upload$"),
            CallbackQueryHandler(cancel_upload, pattern="^cancel_upload$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_upload)],
)

# Define handlers for main.py
handlers = [file_upload_conv_handler]
