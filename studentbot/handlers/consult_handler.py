import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from studentbot.utils.db import get_db, ConsultationRequest
from studentbot.config import ADMIN_CHAT_ID, logger

# States for ConversationHandler
GET_MESSAGE, GET_FILE = range(2)

async def start_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the consultation process.
    """
    await update.message.reply_text(
        "Please describe your consultation request. You can also attach a file (PDF, image, etc.)."
    )
    return GET_MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user's message and file (if any).
    """
    user = update.effective_user
    message_text = update.message.text or update.message.caption

    if not message_text:
        await update.message.reply_text("Please provide a message for your consultation request.")
        return GET_MESSAGE

    context.user_data['consult_message'] = message_text

    file_url = None
    if update.message.document:
        # In a real application, you would download the file and upload it to a cloud storage (e.g., S3)
        # For now, we'll just use the file_id as a placeholder.
        file_url = f"telegram_file_id:{update.message.document.file_id}"
        logger.info(f"User {user.id} uploaded a document with file_id: {update.message.document.file_id}")

    context.user_data['consult_file_url'] = file_url

    db_session = next(get_db())
    new_request = ConsultationRequest(
        user_id=user.id,
        full_name=user.full_name,
        message=message_text,
        file_url=file_url,
        timestamp=datetime.now().isoformat()
    )
    db_session.add(new_request)
    db_session.commit()

    # Notify admin
    admin_message = (
        f"New Consultation Request from {user.full_name} (ID: {user.id}):\n\n"
        f"Message: {message_text}\n"
    )
    if file_url:
        admin_message += f"File: {file_url}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    await update.message.reply_text(
        "Thank you for your consultation request. We will get back to you as soon as possible."
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancels the consultation process.
    """
    await update.message.reply_text("Consultation request cancelled.")
    return ConversationHandler.END

consult_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("consult", start_consultation)],
    states={
        GET_MESSAGE: [MessageHandler(filters.TEXT | filters.Document.ALL, get_message)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

handlers = [consult_conv_handler]
