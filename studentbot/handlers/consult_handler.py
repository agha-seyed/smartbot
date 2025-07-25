from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from utils.text_formatter import sanitize_markdown
from utils.db import save_consultation
from utils.gsheets import save_to_gsheets
from utils.redis_utils import cache_session
from config import ADMIN_CHAT_ID, logger
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

# Stages
FIELD, DEGREE, DESTINATION, LANGUAGE_LEVEL, QUESTION, FILE_UPLOAD = range(6)

async def start_consult(update: Update, context: CallbackContext):
    """Starts the consultation conversation."""
    logger.info(f"User {update.effective_user.id} started a consultation.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(
            sanitize_markdown(texts["consult_intro"]),
            parse_mode="MarkdownV2"
        )
        await query.message.reply_text(
            sanitize_markdown(texts["consult_field"]),
            parse_mode="MarkdownV2"
        )
        context.user_data["consult"] = {
            "name": context.user_data.get("profile", {}).get("name", "")
        }
        return FIELD
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def field(update: Update, context: CallbackContext):
    """Receives the field of study."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data["consult"]["field"] = update.message.text
        keyboard = [
            [
                InlineKeyboardButton(texts["degree_bachelor"], callback_data="bachelor"),
                InlineKeyboardButton(texts["degree_master"], callback_data="master"),
                InlineKeyboardButton(texts["degree_phd"], callback_data="phd")
            ]
        ]
        await update.message.reply_text(
            sanitize_markdown(texts["consult_degree"]),
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return DEGREE
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def degree(update: Update, context: CallbackContext):
    """Receives the degree level."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data["consult"]["degree"] = query.data
        await query.edit_message_text(
            text=f"{texts['consult_degree']}\n{texts[f'degree_{query.data}']}"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=sanitize_markdown(texts["consult_destination"]),
            parse_mode="MarkdownV2"
        )
        return DESTINATION
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def destination(update: Update, context: CallbackContext):
    """Receives the destination country."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data["consult"]["destination"] = update.message.text
        await update.message.reply_text(
            sanitize_markdown(texts["consult_language_level"]),
            parse_mode="MarkdownV2"
        )
        return LANGUAGE_LEVEL
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def language_level(update: Update, context: CallbackContext):
    """Receives the language proficiency level."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data["consult"]["language_level"] = update.message.text
        await update.message.reply_text(
            sanitize_markdown(texts["consult_question"]),
            parse_mode="MarkdownV2"
        )
        return QUESTION
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def question(update: Update, context: CallbackContext):
    """Receives the consultation question."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data["consult"]["question"] = update.message.text
        keyboard = [
            [
                InlineKeyboardButton(texts["yes"], callback_data='yes'),
                InlineKeyboardButton(texts["no"], callback_data='no')
            ]
        ]
        await update.message.reply_text(
            sanitize_markdown(texts["consult_file_prompt"]),
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return FILE_UPLOAD
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def save_consultation_data(update: Update, context: CallbackContext):
    """Saves the consultation data and notifies the admin."""
    logger.info(f"User {update.effective_user.id} saving consultation data.")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        consult_data = context.user_data["consult"]

        # Save data to database
        try:
            save_consultation(consult_data)
            logger.info(f"Consultation data for user {update.effective_user.id} saved to database.")
        except Exception as e:
            logger.error(f"Could not save consultation data for user {update.effective_user.id} to database: {e}")

        # Save data to Google Sheets
        try:
            save_to_gsheets(consult_data, sheet_name="Consultations")
            logger.info(f"Consultation data for user {update.effective_user.id} saved to Google Sheets.")
        except Exception as e:
            logger.error(f"Could not save consultation data for user {update.effective_user.id} to Google Sheets: {e}")

        # Notify admin
        admin_msg = texts["consult_admin_notify"].format(
            name=consult_data["name"],
            field=consult_data["field"],
            degree=consult_data["degree"],
            destination=consult_data["destination"],
            language=consult_data["language_level"],
            question=consult_data["question"],
            file_id=consult_data.get("file_id", "N/A")
        )
        keyboard = [
            [
                InlineKeyboardButton(texts["respond"], callback_data=f"respond_{update.effective_user.id}"),
                InlineKeyboardButton(texts["archive"], callback_data=f"archive_{update.effective_user.id}")
            ]
        ]
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=sanitize_markdown(admin_msg),
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            logger.info(f"Admin notified for new consultation from user {update.effective_user.id}.")
        except Exception as e:
            logger.error(f"Could not notify admin for new consultation from user {update.effective_user.id}: {e}")

        # Confirm to user
        user_msg = texts["consult_confirmation"].format(
            name=consult_data["name"],
            field=consult_data["field"],
            degree=consult_data["degree"],
            destination=consult_data["destination"],
            language=consult_data["language_level"],
            question=consult_data["question"]
        )
        await update.message.reply_text(
            sanitize_markdown(user_msg),
            parse_mode="MarkdownV2"
        )
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text(sanitize_markdown(texts.get("error_message", "Error: Language data is incomplete.")))
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    """Cancels the consultation conversation."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await update.message.reply_text(sanitize_markdown(texts["conversation_cancelled"]))
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Operation cancelled due to an error.")
    return ConversationHandler.END

async def file_upload(update: Update, context: CallbackContext):
    """Handles the file upload decision."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        if query.data == 'yes':
            await query.message.reply_text(sanitize_markdown(texts["consult_upload_file"]))
            return FILE_UPLOAD
        else:
            await save_consultation_data(update, context)
            return ConversationHandler.END
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def save_file(update: Update, context: CallbackContext):
    """Saves the uploaded file and ends the conversation."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        file = update.message.document or update.message.photo or update.message.video
        context.user_data["consult"]["file_id"] = file.file_id
        await save_consultation_data(update, context)
        return ConversationHandler.END
    except AttributeError:
        logger.error(f"Invalid file upload from user {update.effective_user.id}")
        await update.message.reply_text(sanitize_markdown(texts.get("error_message", "Invalid file. Please upload a valid file.")))
        return FILE_UPLOAD
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

consult_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_consult, pattern='^consult$')],
    states={
        FIELD: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, field)],
        DEGREE: [CallbackQueryHandler(degree)],
        DESTINATION: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, destination)],
        LANGUAGE_LEVEL: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, language_level)],
        QUESTION: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, question)],
        FILE_UPLOAD: [
            CallbackQueryHandler(file_upload),
            MessageHandler(Filters.Document.ALL | Filters.PHOTO | Filters.VIDEO, save_file)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True  # تغییر به True برای رفع PTBUserWarning
)
