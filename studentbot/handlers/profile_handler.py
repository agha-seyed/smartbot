from telegram import Update
from telegram.ext import CallbackContext
from utils.db import save_user
from utils.text_formatter import sanitize_markdown
from config import logger
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# States (used by cmd_start)
NAME, FAMILY_NAME, AGE, EMAIL, FIELD_OF_STUDY, COUNTRY = range(6)

async def start_profile_flow(update: Update, context: CallbackContext, first_name: str):
    """Starts the profile creation flow after language selection."""
    logger.info(f"User {update.effective_user.id} starting profile flow.")
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    welcome_message = texts["profile_creation_intro"].format(first_name=first_name)

    if update.callback_query:
        await update.callback_query.message.reply_text(sanitize_markdown(welcome_message))
        await update.callback_query.message.reply_text(sanitize_markdown(texts["profile_name"]))
    else:
        await update.message.reply_text(sanitize_markdown(welcome_message))
        await update.message.reply_text(sanitize_markdown(texts["profile_name"]))

    logger.info(f"Returning state NAME: {NAME}")
    return NAME

async def name(update: Update, context: CallbackContext):
    """Saves name and asks for family name."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile'] = {'name': update.message.text}
    await update.message.reply_text(sanitize_markdown(texts["profile_family_name"]))
    return FAMILY_NAME

async def family_name(update: Update, context: CallbackContext):
    """Saves family name and asks for age."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['family_name'] = update.message.text
    await update.message.reply_text(sanitize_markdown(texts["profile_age"]))
    return AGE

async def age(update: Update, context: CallbackContext):
    """Saves age and asks for email."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['age'] = int(update.message.text)
    await update.message.reply_text(sanitize_markdown(texts["profile_email"]))
    return EMAIL

async def email(update: Update, context: CallbackContext):
    """Saves email and asks for field of study."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['email'] = update.message.text
    await update.message.reply_text(sanitize_markdown(texts["profile_field_of_study"]))
    return FIELD_OF_STUDY

async def field_of_study(update: Update, context: CallbackContext):
    """Saves field of study and asks for country."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['field_of_study'] = update.message.text
    await update.message.reply_text(sanitize_markdown(texts["profile_country"]))
    return COUNTRY

async def country(update: Update, context: CallbackContext):
    """Saves country. The conversation will be ended by the calling handler."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['country'] = update.message.text
    # The save_user call is now handled in the main conversation handler
    # after this function completes.
    await update.message.reply_text(sanitize_markdown(texts["profile_complete"]))
    return -1 # End of this sub-flow, return to parent handler

async def show_profile(update: Update, context: CallbackContext):
    """Displays the user's profile information."""
    logger.info(f"User {update.effective_user.id} requested their profile.")
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    profile = context.user_data.get('profile', {})
    if profile:
        profile_text = f"""
*Name:* {profile.get('name', 'N/A')}
*Family Name:* {profile.get('family_name', 'N/A')}
*Age:* {profile.get('age', 'N/A')}
*Email:* {profile.get('email', 'N/A')}
*Field of Study:* {profile.get('field_of_study', 'N/A')}
*Country:* {profile.get('country', 'N/A')}
        """
        await update.callback_query.message.reply_text(sanitize_markdown(profile_text))
    else:
        logger.warning(f"User {update.effective_user.id} has no profile.")
        await update.callback_query.message.reply_text(sanitize_markdown(texts.get("profile_not_found", "Profile not found.")))
