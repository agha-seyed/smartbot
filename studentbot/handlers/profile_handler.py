from telegram import Update
from telegram.ext import CallbackContext
from utils.db import save_user
from utils.text_formatter import sanitize_markdown
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# States (used by cmd_start)
NAME, FAMILY_NAME, AGE, EMAIL, FIELD_OF_STUDY, COUNTRY = range(6)

async def start_profile_flow(update: Update, context: CallbackContext):
    """Starts the profile creation flow after language selection."""
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    if update.callback_query:
        await update.callback_query.message.reply_text(sanitize_markdown(texts["profile_creation_intro"]))
        await update.callback_query.message.reply_text(sanitize_markdown(texts["profile_name"]))
    else:
        await update.message.reply_text(sanitize_markdown(texts["profile_creation_intro"]))
        await update.message.reply_text(sanitize_markdown(texts["profile_name"]))

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
