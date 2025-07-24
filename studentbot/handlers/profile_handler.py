from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters
from utils.db import save_user
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Stages
NAME, FAMILY_NAME, AGE, EMAIL, FIELD_OF_STUDY, COUNTRY = range(6)

async def start_profile(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(texts["profile_creation_intro"])
    await update.message.reply_text(texts["profile_name"])
    return NAME

async def name(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile'] = {'name': update.message.text}
    await update.message.reply_text(texts["profile_family_name"])
    return FAMILY_NAME

async def family_name(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['family_name'] = update.message.text
    await update.message.reply_text(texts["profile_age"])
    return AGE

async def age(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['age'] = int(update.message.text)
    await update.message.reply_text(texts["profile_email"])
    return EMAIL

async def email(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['email'] = update.message.text
    await update.message.reply_text(texts["profile_field_of_study"])
    return FIELD_OF_STUDY

async def field_of_study(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['field_of_study'] = update.message.text
    await update.message.reply_text(texts["profile_country"])
    return COUNTRY

async def country(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['profile']['country'] = update.message.text

    save_user(context.user_data['profile'])

    await update.message.reply_text(texts["profile_complete"])
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(texts["conversation_cancelled"])
    return ConversationHandler.END

profile_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("profile", start_profile)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
        FAMILY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, family_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
        FIELD_OF_STUDY: [MessageHandler(filters.TEXT & ~filters.COMMAND, field_of_study)],
        COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, country)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
