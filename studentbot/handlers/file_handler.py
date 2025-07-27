# بخش: Handlerهای اصلی
# فایل: file_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from config import logger
import json
import os

from utils.menu_utils import load_texts

def load_files() -> dict:
    """
    Load file list from files.json.

    Returns:
        dict: Dictionary of files or empty dict if file not found.
    """
    try:
        with open("files.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("File files.json not found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in files.json.")
        return {}

async def show_file_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Display a menu of available files (PDFs and videos).
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} requested file menu.")

    try:
        files = load_files()
        keyboard = []
        for pdf_file in files.get("pdfs", []):
            keyboard.append([InlineKeyboardButton(pdf_file["name"], callback_data=f"file_pdf_{pdf_file['name']}")])
        for video_file in files.get("videos", []):
            keyboard.append([InlineKeyboardButton(video_file["name"], callback_data=f"file_video_{video_file['name']}")])

        if not keyboard:
            await query.message.reply_text(
                texts.get("file_menu_empty", "No files available.")
            )
            return

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            texts.get("file_menu_prompt", "Please select a file:"),
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error showing file menu for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send the selected file (PDF or video) to the user.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    try:
        file_type, file_name = query.data.split("_")[1:3]
        file_name = "_".join(query.data.split("_")[2:])  # Handle filenames with underscores
        base_path = "assets/pdfs/" if file_type == "pdf" else "assets/videos/"
        file_path = os.path.join(base_path, file_name)
        logger.info(f"User {user_id} requested file: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            await query.message.reply_text(
                texts.get("file_not_found", f"File {file_name} not found.")
            )
            return

        with open(file_path, "rb") as file:
            if file_type == "pdf":
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file,
                    caption=texts.get("file_sent_caption", f"Here is {file_name}")
                )
            elif file_type == "video":
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=file,
                    caption=texts.get("file_sent_caption", f"Here is {file_name}")
                )
            else:
                logger.error(f"Unsupported file type: {file_type}")
                await query.message.reply_text(
                    texts.get("error_message", "Unsupported file type.")
                )
    except Exception as e:
        logger.error(f"Error sending file {file_name} to user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred while sending the file.")
        )

# Define handlers for main.py
handlers = [
    CallbackQueryHandler(show_file_menu, pattern="^file$"),
    CallbackQueryHandler(send_file, pattern="^file_(pdf|video)_"),
]
