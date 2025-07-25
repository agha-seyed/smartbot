from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
)
from config import ADMIN_CHAT_ID, logger
from utils.db import get_all_users
import json

def load_texts(lang):
    """Load language-specific texts from JSON files."""
    try:
        with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Language file lang/{lang}.json not found.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in lang/{lang}.json.")
        raise

def load_files():
    """Loads the files from the files.json file."""
    try:
        with open('files.json', 'r', encoding='utf-8') as f:  # اصلاح مسیر
            return json.load(f)
    except FileNotFoundError:
        logger.error("File files.json not found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in files.json.")
        raise

def save_files(files):
    """Saves the files to the files.json file."""
    try:
        with open('files.json', 'w', encoding='utf-8') as f:  # اصلاح مسیر
            json.dump(files, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Could not save files to files.json: {e}")
        raise

def is_admin(update: Update) -> bool:
    """Checks if the user is an admin."""
    return str(update.effective_user.id) == ADMIN_CHAT_ID

async def add_file(update: Update, context: CallbackContext):
    """Adds a file to the file list."""
    logger.info(f"User {update.effective_user.id} trying to add a file with args: {context.args}")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        if not is_admin(update):
            logger.warning(f"User {update.effective_user.id} is not an admin.")
            await update.message.reply_text(texts["admin_not_authorized"])
            return

        if len(context.args) != 2:
            logger.warning(f"User {update.effective_user.id} used /addfile with wrong number of arguments.")
            await update.message.reply_text(texts["admin_add_file_usage"])
            return

        file_type, file_name = context.args
        files = load_files()

        if file_type not in files:
            files[file_type] = []

        files[file_type].append(file_name)
        save_files(files)
        logger.info(f"File '{file_name}' added to '{file_type}'.")
        await update.message.reply_text(texts["admin_file_added"].format(file_name=file_name, file_type=file_type))
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))
    except Exception as e:
        logger.error(f"Error adding file for user {update.effective_user.id}: {e}")
        await update.message.reply_text(texts.get("error_message", "An error occurred. Please try again."))

async def remove_file(update: Update, context: CallbackContext):
    """Removes a file from the file list."""
    logger.info(f"User {update.effective_user.id} trying to remove a file with args: {context.args}")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        if not is_admin(update):
            logger.warning(f"User {update.effective_user.id} is not an admin.")
            await update.message.reply_text(texts["admin_not_authorized"])
            return

        if len(context.args) != 2:
            logger.warning(f"User {update.effective_user.id} used /removefile with wrong number of arguments.")
            await update.message.reply_text(texts["admin_remove_file_usage"])
            return

        file_type, file_name = context.args
        files = load_files()

        if file_type in files and file_name in files[file_type]:
            files[file_type].remove(file_name)
            save_files(files)
            logger.info(f"File '{file_name}' removed from '{file_type}'.")
            await update.message.reply_text(texts["admin_file_removed"].format(file_name=file_name, file_type=file_type))
        else:
            logger.warning(f"File '{file_name}' not found in '{file_type}'.")
            await update.message.reply_text(texts["admin_file_not_found"].format(file_name=file_name, file_type=file_type))
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))
    except Exception as e:
        logger.error(f"Error removing file for user {update.effective_user.id}: {e}")
        await update.message.reply_text(texts.get("error_message", "An error occurred. Please try again."))

async def broadcast(update: Update, context: CallbackContext):
    """Broadcasts a message to all users."""
    logger.info(f"User {update.effective_user.id} trying to broadcast a message: {context.args}")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        if not is_admin(update):
            logger.warning(f"User {update.effective_user.id} is not an admin.")
            await update.message.reply_text(texts["admin_not_authorized"])
            return

        message = " ".join(context.args)
        if not message:
            logger.warning(f"User {update.effective_user.id} used /broadcast with no message.")
            await update.message.reply_text(texts["admin_broadcast_usage"])
            return

        users = get_all_users()
        logger.info(f"Broadcasting message to {len(users)} users.")
        for user in users:
            try:
                await context.bot.send_message(chat_id=user.id, text=message)
            except Exception as e:
                logger.error(f"Could not send message to user {user.id}: {e}")

        await update.message.reply_text(texts["admin_broadcast_success"].format(user_count=len(users)))
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))
    except Exception as e:
        logger.error(f"Error broadcasting message for user {update.effective_user.id}: {e}")
        await update.message.reply_text(texts.get("error_message", "An error occurred. Please try again."))

async def schedule(update: Update, context: CallbackContext):
    """Schedules a message to be sent to all users."""
    logger.info(f"User {update.effective_user.id} trying to schedule a message: {context.args}")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        if not is_admin(update):
            logger.warning(f"User {update.effective_user.id} is not an admin.")
            await update.message.reply_text(texts["admin_not_authorized"])
            return

        try:
            time_str = context.args[0]
            message = " ".join(context.args[1:])
            send_time = datetime.strptime(time_str, "%Y-%m-%d-%H:%M")
        except (ValueError, IndexError):
            logger.warning(f"User {update.effective_user.id} used /schedule with wrong format.")
            await update.message.reply_text(texts["admin_schedule_usage"])
            return

        users = get_all_users()
        logger.info(f"Scheduling message to be sent at {send_time} to {len(users)} users.")
        for user in users:
            context.job_queue.run_once(
                lambda ctx: ctx.bot.send_message(chat_id=user.id, text=message),
                send_time
            )

        await update.message.reply_text(texts["admin_schedule_success"].format(send_time=send_time, user_count=len(users)))
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))
    except Exception as e:
        logger.error(f"Error scheduling message for user {update.effective_user.id}: {e}")
        await update.message.reply_text(texts.get("error_message", "An error occurred. Please try again."))

async def poll(update: Update, context: CallbackContext):
    """Creates a poll."""
    logger.info(f"User {update.effective_user.id} trying to create a poll: {context.args}")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        if not is_admin(update):
            logger.warning(f"User {update.effective_user.id} is not an admin.")
            await update.message.reply_text(texts["admin_not_authorized"])
            return

        try:
            question = context.args[0]
            options = context.args[1:]
        except IndexError:
            logger.warning(f"User {update.effective_user.id} used /poll with wrong format.")
            await update.message.reply_text(texts["admin_poll_usage"])
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

        await update.message.reply_text(texts["admin_poll_success"].format(user_count=len(users)))
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))
    except Exception as e:
        logger.error(f"Error creating poll for user {update.effective_user.id}: {e}")
        await update.message.reply_text(texts.get("error_message", "An error occurred. Please try again."))

async def admin_menu(update: Update, context: CallbackContext):
    """Shows the admin menu."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        if not is_admin(update):
            logger.warning(f"User {update.effective_user.id} is not an admin.")
            await update.message.reply_text(texts["admin_not_authorized"])
            return

        keyboard = [
            [InlineKeyboardButton(texts["admin_menu_add_file"], callback_data='admin_add_file')],
            [InlineKeyboardButton(texts["admin_menu_remove_file"], callback_data='admin_remove_file')],
            [InlineKeyboardButton(texts["admin_menu_broadcast"], callback_data='admin_broadcast')],
            [InlineKeyboardButton(texts["admin_menu_schedule"], callback_data='admin_schedule')],
            [InlineKeyboardButton(texts["admin_menu_poll"], callback_data='admin_poll')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(texts["admin_menu_title"], reply_markup=reply_markup)
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))

async def admin_add_file_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to add a file."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(texts["admin_add_file_usage"])
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))

async def admin_remove_file_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to remove a file."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(texts["admin_remove_file_usage"])
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))

async def admin_broadcast_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to broadcast a message."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(texts["admin_broadcast_usage"])
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))

async def admin_schedule_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to schedule a message."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(texts["admin_schedule_usage"])
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))

async def admin_poll_prompt(update: Update, context: CallbackContext):
    """Prompts the admin to create a poll."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(texts["admin_poll_usage"])
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text(texts.get("error_message", "Error: Language data is incomplete."))

admin_handler = CommandHandler("admin", admin_menu)
add_file_handler = CommandHandler("addfile", add_file)
remove_file_handler = CommandHandler("removefile", remove_file)
broadcast_handler = CommandHandler("broadcast", broadcast)
schedule_handler = CommandHandler("schedule", schedule)
poll_handler = CommandHandler("poll", poll)

admin_menu_handlers = [
    CallbackQueryHandler(admin_add_file_prompt, pattern='^admin_add_file$'),
    CallbackQueryHandler(admin_remove_file_prompt, pattern='^admin_remove_file$'),
    CallbackQueryHandler(admin_broadcast_prompt, pattern='^admin_broadcast$'),
    CallbackQueryHandler(admin_schedule_prompt, pattern='^admin_schedule$'),
    CallbackQueryHandler(admin_poll_prompt, pattern='^admin_poll$'),
]
