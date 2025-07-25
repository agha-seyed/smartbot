from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from config import ADMIN_CHAT_ID, logger
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
    logger.info(f"User {update.effective_user.id} trying to add a file with args: {context.args}")
    if not is_admin(update):
        logger.warning(f"User {update.effective_user.id} is not an admin.")
        return

    if len(context.args) != 2:
        logger.warning(f"User {update.effective_user.id} used /addfile with wrong number of arguments.")
        await update.message.reply_text("Usage: /addfile <file_type> <file_name>")
        return

    file_type, file_name = context.args
    files = load_files()

    if file_type not in files:
        files[file_type] = []

    files[file_type].append(file_name)
    save_files(files)
    logger.info(f"File '{file_name}' added to '{file_type}'.")
    await update.message.reply_text(f"File '{file_name}' added to '{file_type}'.")

async def remove_file(update: Update, context: CallbackContext):
    """Removes a file from the file list."""
    logger.info(f"User {update.effective_user.id} trying to remove a file with args: {context.args}")
    if not is_admin(update):
        logger.warning(f"User {update.effective_user.id} is not an admin.")
        return

    if len(context.args) != 2:
        logger.warning(f"User {update.effective_user.id} used /removefile with wrong number of arguments.")
        await update.message.reply_text("Usage: /removefile <file_type> <file_name>")
        return

    file_type, file_name = context.args
    files = load_files()

    if file_type in files and file_name in files[file_type]:
        files[file_type].remove(file_name)
        save_files(files)
        logger.info(f"File '{file_name}' removed from '{file_type}'.")
        await update.message.reply_text(f"File '{file_name}' removed from '{file_type}'.")
    else:
        logger.warning(f"File '{file_name}' not found in '{file_type}'.")
        await update.message.reply_text(f"File '{file_name}' not found in '{file_type}'.")

async def broadcast(update: Update, context: CallbackContext):
    """Broadcasts a message to all users."""
    logger.info(f"User {update.effective_user.id} trying to broadcast a message: {context.args}")
    if not is_admin(update):
        logger.warning(f"User {update.effective_user.id} is not an admin.")
        return

    message = " ".join(context.args)
    if not message:
        logger.warning(f"User {update.effective_user.id} used /broadcast with no message.")
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    users = get_all_users()
    logger.info(f"Broadcasting message to {len(users)} users.")
    for user in users:
        try:
            await context.bot.send_message(chat_id=user.id, text=message)
        except Exception as e:
            logger.error(f"Could not send message to user {user.id}: {e}")

    await update.message.reply_text(f"Message broadcasted to {len(users)} users.")

async def admin_menu(update: Update, context: CallbackContext):
    """Shows the admin menu."""
    if not is_admin(update):
        return

    keyboard = [
        [InlineKeyboardButton("Add File", callback_data='admin_add_file')],
        [InlineKeyboardButton("Remove File", callback_data='admin_remove_file')],
        [InlineKeyboardButton("Broadcast Message", callback_data='admin_broadcast')],
        [InlineKeyboardButton("Schedule Message", callback_data='admin_schedule')],
        [InlineKeyboardButton("Create Poll", callback_data='admin_poll')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin Menu:", reply_markup=reply_markup)

async def admin_add_file_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to add a file."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please use the format: /addfile <file_type> <file_name>")

async def admin_remove_file_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to remove a file."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please use the format: /removefile <file_type> <file_name>")

async def admin_broadcast_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to broadcast a message."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please use the format: /broadcast <message>")

admin_handler = CommandHandler("admin", admin_menu)
add_file_handler = CommandHandler("addfile", add_file)
remove_file_handler = CommandHandler("removefile", remove_file)
from datetime import datetime, timedelta

async def schedule(update: Update, context: CallbackContext):
    """Schedules a message to be sent to all users."""
    logger.info(f"User {update.effective_user.id} trying to schedule a message: {context.args}")
    if not is_admin(update):
        logger.warning(f"User {update.effective_user.id} is not an admin.")
        return

    try:
        time_str = context.args[0]
        message = " ".join(context.args[1:])
        send_time = datetime.strptime(time_str, "%Y-%m-%d-%H:%M")
    except (ValueError, IndexError):
        logger.warning(f"User {update.effective_user.id} used /schedule with wrong format.")
        await update.message.reply_text("Usage: /schedule YYYY-MM-DD-HH:MM <message>")
        return

    users = get_all_users()
    logger.info(f"Scheduling message to be sent at {send_time} to {len(users)} users.")
    for user in users:
        context.job_queue.run_once(
            lambda ctx: ctx.bot.send_message(chat_id=user.id, text=message),
            send_time
        )

    await update.message.reply_text(f"Message scheduled to be sent at {send_time} to {len(users)} users.")

async def poll(update: Update, context: CallbackContext):
    """Creates a poll."""
    logger.info(f"User {update.effective_user.id} trying to create a poll: {context.args}")
    if not is_admin(update):
        logger.warning(f"User {update.effective_user.id} is not an admin.")
        return

    try:
        question = context.args[0]
        options = context.args[1:]
    except IndexError:
        logger.warning(f"User {update.effective_user.id} used /poll with wrong format.")
        await update.message.reply_text("Usage: /poll <question> <option1> <option2> ...")
        return

    users = get_all_users()
    logger.info(f"Sending poll to {len(users)} users.")
    for user in users:
        try:
            await context.bot.send_poll(
                chat_id=user.id,
                question=question,
                options=options,
                is_anonymous=False,
                allows_multiple_answers=False,
            )
        except Exception as e:
            logger.error(f"Could not send poll to user {user.id}: {e}")

    await update.message.reply_text(f"Poll sent to {len(users)} users.")

broadcast_handler = CommandHandler("broadcast", broadcast)
schedule_handler = CommandHandler("schedule", schedule)
poll_handler = CommandHandler("poll", poll)

async def admin_schedule_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to schedule a message."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please use the format: /schedule YYYY-MM-DD-HH:MM <message>")

async def admin_poll_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to create a poll."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please use the format: /poll <question> <option1> <option2> ...")

admin_menu_handlers = [
    CallbackQueryHandler(admin_add_file_prompt, pattern='^admin_add_file$'),
    CallbackQueryHandler(admin_remove_file_prompt, pattern='^admin_remove_file$'),
    CallbackQueryHandler(admin_broadcast_prompt, pattern='^admin_broadcast$'),
    CallbackQueryHandler(admin_schedule_prompt, pattern='^admin_schedule$'),
    CallbackQueryHandler(admin_poll_prompt, pattern='^admin_poll$'),
]
