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
from config import logger
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
FAMILY_MEMBERS, ANNUAL_INCOME, PROPERTY_OWNERSHIP, PROPERTY_SIZE = range(4)

async def start_isee_calculation(update: Update, context: CallbackContext):
    """Starts the ISEE calculation conversation."""
    logger.info(f"User {update.effective_user.id} started ISEE calculation.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await query.message.reply_text(sanitize_markdown(texts["isee_intro"]))
        await query.message.reply_text(sanitize_markdown(texts["isee_family_members"]))
        return FAMILY_MEMBERS
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def family_members(update: Update, context: CallbackContext):
    """Receives the number of family members."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data['isee'] = {'family_members': int(update.message.text)}
        await update.message.reply_text(sanitize_markdown(texts["isee_annual_income"]))
        return ANNUAL_INCOME
    except ValueError:
        logger.error(f"Invalid input for family members from user {update.effective_user.id}")
        await update.message.reply_text(sanitize_markdown(texts.get("error_message", "Invalid input. Please enter a number.")))
        return FAMILY_MEMBERS
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def annual_income(update: Update, context: CallbackContext):
    """Receives the annual income."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data['isee']['annual_income'] = float(update.message.text)
        keyboard = [
            [InlineKeyboardButton(texts["property_owner"], callback_data='owner')],
            [InlineKeyboardButton(texts["property_tenant"], callback_data='tenant')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(sanitize_markdown(texts["isee_property_ownership"]), reply_markup=reply_markup)
        return PROPERTY_OWNERSHIP
    except ValueError:
        logger.error(f"Invalid input for annual income from user {update.effective_user.id}")
        await update.message.reply_text(sanitize_markdown(texts.get("error_message", "Invalid input. Please enter a number.")))
        return ANNUAL_INCOME
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def property_ownership(update: Update, context: CallbackContext):
    """Receives property ownership status."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data['isee']['property_ownership'] = query.data
        if query.data == 'owner':
            await query.edit_message_text(text=sanitize_markdown(texts["isee_property_size"]))
            return PROPERTY_SIZE
        else:
            await calculate_and_show_isee(update, context)
            return ConversationHandler.END
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await query.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def property_size(update: Update, context: CallbackContext):
    """Receives property size and calculates ISEE."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        context.user_data['isee']['property_size'] = float(update.message.text)
        await calculate_and_show_isee(update, context)
        return ConversationHandler.END
    except ValueError:
        logger.error(f"Invalid input for property size from user {update.effective_user.id}")
        await update.message.reply_text(sanitize_markdown(texts.get("error_message", "Invalid input. Please enter a number.")))
        return PROPERTY_SIZE
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Error: Language data is incomplete.")
        return ConversationHandler.END

async def calculate_and_show_isee(update: Update, context: CallbackContext):
    """Calculates and displays the ISEE result."""
    logger.info(f"User {update.effective_user.id} calculating ISEE.")
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        isee_data = context.user_data['isee']

        family_members = isee_data['family_members']
        annual_income = isee_data['annual_income']
        property_ownership = isee_data['property_ownership']
        property_size = isee_data.get('property_size', 0)

        property_value = property_size * 500 * 0.2 if property_ownership == 'owner' else 0

        household_coefficient = 1
        if family_members == 2:
            household_coefficient = 1.57
        elif family_members == 3:
            household_coefficient = 2.04
        elif family_members == 4:
            household_coefficient = 2.46
        elif family_members >= 5:
            household_coefficient = 2.85

        isee = (annual_income + property_value) / household_coefficient
        logger.info(f"User {update.effective_user.id} ISEE calculated: {isee}")

        scholarship_status = texts["scholarship_none"]
        if isee <= 27948.60:
            if isee <= (27948.60 * 0.55):
                scholarship_status = texts["scholarship_full"]
            elif isee <= (27948.60 * 0.715):
                scholarship_status = texts["scholarship_medium"]
            else:
                scholarship_status = texts["scholarship_partial"]

        result_text = texts["isee_result"].format(
            family_members=family_members,
            annual_income=annual_income,
            property_ownership=texts[f"property_{property_ownership}"],
            isee=f"{isee:.2f}",
            scholarship_status=scholarship_status
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=sanitize_markdown(result_text),
            parse_mode="MarkdownV2"
        )
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=sanitize_markdown(texts.get("error_message", "Error: Language data is incomplete.")),
            parse_mode="MarkdownV2"
        )

async def cancel(update: Update, context: CallbackContext):
    """Cancels the ISEE calculation conversation."""
    lang = context.user_data.get("lang", "fa")
    try:
        texts = load_texts(lang)
        await update.message.reply_text(sanitize_markdown(texts["conversation_cancelled"]))
    except KeyError as e:
        logger.error(f"Missing key in language file for {lang}: {e}")
        await update.message.reply_text("Operation cancelled due to an error.")
    return ConversationHandler.END

isee_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_isee_calculation, pattern='^isee$')],
    states={
        FAMILY_MEMBERS: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, family_members)],
        ANNUAL_INCOME: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, annual_income)],
        PROPERTY_OWNERSHIP: [CallbackQueryHandler(property_ownership)],
        PROPERTY_SIZE: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, property_size)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True  # تغییر به True برای رفع PTBUserWarning
)
