from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

async def menu(update: Update, context: CallbackContext):
    await update.message.reply_text("This is a placeholder for the main menu.")

menu_handler = CommandHandler("menu", menu)
