from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from config import ADMIN_CHAT_ID
from utils.db import get_all_users
import json

def is_admin(update: Update) -> bool:
    """Checks if the user is an admin."""
    return str(update.effective_user.id) == ADMIN_CHAT_ID

def load_files():
    """Loads the files from the files.json file."""
    with open('studentbot/files.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_files(files):
    """Saves the files to the files.json file."""
    with open('studentbot/files.json', 'w', encoding='utf-8') as f:
        json.dump(files, f, indent=4)

async def add_file(update: Update, context: CallbackContext):
    """Adds a file to the file list."""
    if not is_admin(update):
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /addfile <file_type> <file_name>")
        return

    file_type, file_name = context.args
    files = load_files()

    if file_type not in files:
        files[file_type] = []

    files[file_type].append(file_name)
    save_files(files)
    await update.message.reply_text(f"File '{file_name}' added to '{file_type}'.")

async def remove_file(update: Update, context: CallbackContext):
    """Removes a file from the file list."""
    if not is_admin(update):
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /removefile <file_type> <file_name>")
        return

    file_type, file_name = context.args
    files = load_files()

    if file_type in files and file_name in files[file_type]:
        files[file_type].remove(file_name)
        save_files(files)
        await update.message.reply_text(f"File '{file_name}' removed from '{file_type}'.")
    else:
        await update.message.reply_text(f"File '{file_name}' not found in '{file_type}'.")

async def broadcast(update: Update, context: CallbackContext):
    """Broadcasts a message to all users."""
    if not is_admin(update):
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    users = get_all_users()
    for user in users:
        try:
            await context.bot.send_message(chat_id=user.id, text=message)
        except Exception as e:
            print(f"Could not send message to user {user.id}: {e}")

    await update.message.reply_text(f"Message broadcasted to {len(users)} users.")

add_file_handler = CommandHandler("addfile", add_file)
remove_file_handler = CommandHandler("removefile", remove_file)
broadcast_handler = CommandHandler("broadcast", broadcast)
