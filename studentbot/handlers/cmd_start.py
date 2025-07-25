from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode
from . import profile_handler, gamification_handler
import json

# --- Load all language texts ---
def load_all_texts():
    texts = {}
    for lang in ["en", "fa", "it"]:
        with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
            texts[lang] = json.load(f)
    return texts

all_texts = load_all_texts()

# --- Conversation States ---
SELECTING_LANG, REGISTERING_PROFILE = range(2)
# Profile states are imported from profile_handler
NAME, FAMILY_NAME, AGE, EMAIL, FIELD_OF_STUDY, COUNTRY = profile_handler.NAME, profile_handler.FAMILY_NAME, profile_handler.AGE, profile_handler.EMAIL, profile_handler.FIELD_OF_STUDY, profile_handler.COUNTRY


# --- Welcome Message Handler ---
async def start(update: Update, context: CallbackContext):
    """Sends the initial welcome message and language selection."""
    welcome_text = (
        f"{all_texts['fa']['welcome_message']}\n\n"
        f"{all_texts['en']['welcome_message']}\n\n"
        f"{all_texts['it']['welcome_message']}"
    )
    keyboard = [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data='lang_fa'),
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇮🇹 Italiano", callback_data='lang_it'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return SELECTING_LANG

# --- Main Menu Display ---
async def show_main_menu(update: Update, context: CallbackContext):
    """Displays the main menu with a 2-column layout."""
    lang_code = context.user_data.get('lang', 'fa')
    texts = all_texts[lang_code]
    keyboard = [
        [
            InlineKeyboardButton(texts["profile_button"], callback_data='profile'),
            InlineKeyboardButton(texts["isee_button"], callback_data='isee')
        ],
        [
            InlineKeyboardButton(texts["consult_button"], callback_data='consult'),
            InlineKeyboardButton(texts["question_button"], callback_data='question')
        ],
        [
            InlineKeyboardButton(texts["weather_button"], callback_data='weather'),
            InlineKeyboardButton(texts["apps_guide_button"], callback_data='apps_guide')
        ],
        [
            InlineKeyboardButton(texts["search_button"], callback_data='search'),
            InlineKeyboardButton(texts["file_button"], callback_data='file')
        ],
        [
            InlineKeyboardButton(texts["gamification_button"], callback_data='gamification'),
            InlineKeyboardButton(texts["location_button"], callback_data='location')
        ],
        [
            InlineKeyboardButton(texts["live_chat_button"], callback_data='live_chat')
        ],
        [
            InlineKeyboardButton(texts["scholarships_button"], callback_data='scholarships'),
            InlineKeyboardButton(texts["migration_steps_button"], callback_data='migration_steps')
        ],
        [
            InlineKeyboardButton(texts["housing_button"], callback_data='housing'),
            InlineKeyboardButton(texts["student_life_button"], callback_data='student_life')
        ],
        [
            InlineKeyboardButton(texts["universities_button"], callback_data='universities'),
            InlineKeyboardButton(texts["tools_button"], callback_data='tools')
        ],
        [
            InlineKeyboardButton(texts["language_courses_button"], callback_data='language_courses'),
            InlineKeyboardButton(texts["university_news_button"], callback_data='university_news')
        ],
        [
            InlineKeyboardButton(texts["user_feedback_button"], callback_data='user_feedback')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send as a new message
    await update.message.reply_text(
        text=texts.get("main_menu_title", "Main Menu"),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# --- Language Selection and Registration Flow ---
async def language_select_and_start_registration(update: Update, context: CallbackContext):
    """Handles language selection and transitions to the registration process."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang_code = query.data.split('_')[1]
    context.user_data['lang'] = lang_code

    # Clean up the language selection message
    await query.edit_message_text(text=all_texts[lang_code]['welcome_message'], parse_mode=ParseMode.HTML)

    # Start the profile flow
    return await profile_handler.start_profile_flow(update, context, user.first_name)

from utils.db import save_user

async def registration_complete(update: Update, context: CallbackContext):
    """Called after the last piece of profile info is provided."""
    await profile_handler.country(update, context) # Process the final input
    save_user(context.user_data['profile'])
    gamification_handler.add_points(update.effective_user.id, 10)
    await show_main_menu(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    """Cancels the conversation."""
    lang_code = context.user_data.get('lang', 'fa')
    await update.message.reply_text(all_texts[lang_code].get("conversation_cancelled", "Operation cancelled."))
    return ConversationHandler.END


# --- The main conversation handler for onboarding ---
onboarding_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECTING_LANG: [CallbackQueryHandler(language_select_and_start_registration, pattern='^lang_')],
        # Registration states
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_handler.name)],
        FAMILY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_handler.family_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_handler.age)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_handler.email)],
        FIELD_OF_STUDY: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_handler.field_of_study)],
        COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, registration_complete)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
