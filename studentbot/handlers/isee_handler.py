# بخش: Handlerهای اصلی
# فایل: isee_handler.py (نسخه بهبودیافته)

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
from config import logger, ADMIN_CHAT_ID
from utils.gsheets import append_to_sheet
from utils.db import get_db, User
from sqlalchemy.orm import Session
from datetime import datetime
import json

# States for ConversationHandler
INCOME, ASSETS, FAMILY_MEMBERS, CONFIRM = range(4)

def load_texts(lang: str) -> dict:
    """
    Load language-specific texts from JSON files.

    Args:
        lang (str): Language code (e.g., 'en', 'fa', 'it').

    Returns:
        dict: Language texts or empty dict if file not found.
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

async def start_isee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the ISEE calculation process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started ISEE calculation.")

    # Check if user has a profile
    db: Session = next(get_db())
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        await update.message.reply_text(
            texts.get("no_profile", "Please create your profile first using /profile.")
        )
        return ConversationHandler.END

    context.user_data["user_profile"] = {
        "first_name": user.first_name,
        "family_name": user.family_name,
        "age": user.age,
        "email": user.email,
        "field_of_study": user.field_of_study,
        "country": user.country
    }

    await update.message.reply_text(
        texts.get("isee_intro", "Let's calculate your ISEE. Please enter your annual family income (in EUR):")
    )
    return INCOME

async def get_income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's annual family income.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    income_text = update.message.text.strip()

    try:
        income = float(income_text)
        if income < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid income (non-negative number in EUR).")
        )
        return INCOME

    context.user_data["isee_income"] = income
    logger.info(f"User {user_id} entered income: {income}")
    await update.message.reply_text(
        texts.get("isee_assets", "Please enter your total family assets (in EUR):")
    )
    return ASSETS

async def get_assets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's total family assets.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    assets_text = update.message.text.strip()

    try:
        assets = float(assets_text)
        if assets < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            texts.get("error_message", "Please enter valid assets (non-negative number in EUR).")
        )
        return ASSETS

    context.user_data["isee_assets"] = assets
    logger.info(f"User {user_id} entered assets: {assets}")
    await update.message.reply_text(
        texts.get("isee_family_members", "How many members are in your family?")
    )
    return FAMILY_MEMBERS

async def get_family_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the number of family members.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    members_text = update.message.text.strip()

    try:
        members = int(members_text)
        if members < 1 or members > 20:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid number of family members (1-20).")
        )
        return FAMILY_MEMBERS

    context.user_data["isee_family_members"] = members
    logger.info(f"User {user_id} entered family members: {members}")

    # ISEE calculation
    income = context.user_data["isee_income"]
    assets = context.user_data["isee_assets"]

    # ISP (Indicatore della Situazione Patrimoniale)
    isp = assets * 0.2

    # ISR (Indicatore della Situazione Reddituale)
    isr = income

    # Scale di equivalenza
    scale = {
        1: 1,
        2: 1.57,
        3: 2.04,
        4: 2.46,
        5: 2.85,
    }
    equivalence_parameter = scale.get(members, 2.85 + 0.35 * (members - 5))

    # ISEE
    isee = (isr + isp) / equivalence_parameter
    context.user_data["isee_result"] = round(isee, 2)

    # Scholarship status
    if isee <= 13000:
        scholarship_status = texts.get("scholarship_full", "Full scholarship")
    elif isee <= 23000:
        scholarship_status = texts.get("scholarship_partial", "Partial scholarship")
    else:
        scholarship_status = texts.get("scholarship_none", "Not eligible for scholarship")
    context.user_data["scholarship_status"] = scholarship_status

    # Prepare summary with profile
    profile = context.user_data["user_profile"]
    isee_summary = (
        f"{texts.get('profile_name', 'Name')}: {profile['first_name']}\n"
        f"{texts.get('profile_family_name', 'Family Name')}: {profile['family_name']}\n"
        f"{texts.get('profile_age', 'Age')}: {profile['age']}\n"
        f"{texts.get('profile_email', 'Email')}: {profile['email']}\n"
        f"{texts.get('profile_field_of_study', 'Field of Study')}: {profile['field_of_study']}\n"
        f"{texts.get('profile_country', 'Country')}: {profile['country']}\n"
        f"{texts.get('isee_income', 'Income')}: {income} EUR\n"
        f"{texts.get('isee_assets', 'Assets')}: {assets} EUR\n"
        f"{texts.get('isee_family_members', 'Family Members')}: {members}\n"
        f"{texts.get('isee_result', 'Estimated ISEE')}: {isee} EUR\n"
        f"{texts.get('scholarship_status_label', 'Scholarship Status')}: {context.user_data['scholarship_status']}"
    )
    keyboard = [
        [
            InlineKeyboardButton(texts.get("yes", "Yes"), callback_data="confirm_isee"),
            InlineKeyboardButton(texts.get("no", "No"), callback_data="cancel_isee"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("isee_confirm", "Please confirm your ISEE data:") + "\n\n" + isee_summary,
        reply_markup=reply_markup
    )
    return CONFIRM

async def confirm_isee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the ISEE data to Google Sheets and database, notify admin, and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    income = context.user_data["isee_income"]
    assets = context.user_data["isee_assets"]
    members = context.user_data["isee_family_members"]
    isee = context.user_data["isee_result"]
    profile = context.user_data["user_profile"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"User {user_id} confirmed ISEE data.")

    try:
        # Save to Google Sheets
        data = [
            user_id,
            profile["first_name"] or "",
            profile["family_name"] or "",
            profile["age"] or "",
            profile["email"] or "",
            profile["field_of_study"] or "",
            profile["country"] or "",
            income,
            assets,
            timestamp
        ]
        append_to_sheet("StudentBotQuestions", data)

        # Save ISEE to database
        db: Session = next(get_db())
        user = db.query(User).filter_by(user_id=user_id).first()
        user.isee = isee
        db.commit()

        # Notify admin
        admin_message = (
            texts.get("isee_admin_notify", "New ISEE calculation submitted:\n")
            + f"User ID: {user_id}\n"
            + f"Name: {profile['first_name']} {profile['family_name']}\n"
            + f"Age: {profile['age']}\n"
            + f"Email: {profile['email']}\n"
            + f"Field of Study: {profile['field_of_study']}\n"
            + f"Country: {profile['country']}\n"
            + f"Income: {income} EUR\n"
            + f"Assets: {assets} EUR\n"
            + f"Family Members: {members}\n"
            + f"Estimated ISEE: {isee} EUR\n"
            + f"Time: {timestamp}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await query.message.reply_text(
            texts.get("isee_submitted", "Your ISEE data has been submitted successfully!")
        )
    except Exception as e:
        logger.error(f"Error saving ISEE data for user {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    # Clear ISEE data
    for key in ["isee_income", "isee_assets", "isee_family_members", "isee_result", "user_profile"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

async def cancel_isee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel ISEE calculation and end the conversation.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled ISEE calculation.")

    await query.message.reply_text(
        texts.get("conversation_cancelled", "ISEE calculation cancelled.")
    )

    # Clear ISEE data
    for key in ["isee_income", "isee_assets", "isee_family_members", "isee_result", "user_profile"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END

# Define ConversationHandler
isee_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("isee", start_isee)],
    states={
        INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_income)],
        ASSETS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_assets)],
        FAMILY_MEMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_family_members)],
        CONFIRM: [
            CallbackQueryHandler(confirm_isee, pattern="^confirm_isee$"),
            CallbackQueryHandler(cancel_isee, pattern="^cancel_isee$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_isee)],
)

# Define handlers for main.py
handlers = [isee_conv_handler]
