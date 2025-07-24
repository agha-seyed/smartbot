from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import json

# --- Load all language texts ---
def load_all_texts():
    texts = {}
    for lang in ["en", "fa", "it"]:
        with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
            texts[lang] = json.load(f)
    return texts

all_texts = load_all_texts()

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

# --- Main Menu Display ---
async def show_main_menu(update: Update, context: CallbackContext, lang_code: str):
    """Displays the main menu with a 2-column layout."""
    texts = all_texts[lang_code]
    keyboard = [
        [
            InlineKeyboardButton(texts.get("menu_scholarships", "📚-"), callback_data='menu_scholarships'),
            InlineKeyboardButton(texts.get("menu_migration", "🛂-"), callback_data='menu_migration'),
        ],
        [
            InlineKeyboardButton(texts.get("menu_housing", "🏠-"), callback_data='menu_housing'),
            InlineKeyboardButton(texts.get("menu_student_life", "🎓-"), callback_data='menu_student_life'),
        ],
        [
            InlineKeyboardButton(texts.get("menu_universities", "🏛️-"), callback_data='menu_universities'),
            InlineKeyboardButton(texts.get("menu_isee_calculator", "💰-"), callback_data='isee_calculator'),
        ],
        [
            InlineKeyboardButton(texts.get("menu_weather", "🌤️-"), callback_data='weather'),
            InlineKeyboardButton(texts.get("menu_ask_question", "❓-"), callback_data='ask_question'),
        ],
        [
            InlineKeyboardButton(texts.get("menu_profile", "👤-"), callback_data='profile'),
            InlineKeyboardButton(texts.get("menu_settings", "⚙️-"), callback_data='settings'),
        ],
        [
             InlineKeyboardButton(texts.get("menu_apps_guide", "📲-"), callback_data='apps_entry_guide')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # For a new message after language selection
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text=texts.get("main_menu_title", "Main Menu"),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    # For returning to menu
    else:
        await update.message.reply_text(
            text=texts.get("main_menu_title", "Main Menu"),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

# --- Language Selection and Registration Flow ---
async def language_select_and_register(update: Update, context: CallbackContext):
    """Handles language selection and starts the registration process."""
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split('_')[1]
    context.user_data['lang'] = lang_code

    # For now, just show the main menu. Registration will be the next step.
    await show_main_menu(update, context, lang_code)


# --- Placeholder for buttons under construction ---
async def placeholder_handler(update: Update, context: CallbackContext):
    """Generic handler for features under construction."""
    query = update.callback_query
    await query.answer()
    lang_code = context.user_data.get('lang', 'fa')
    await query.message.reply_text(all_texts[lang_code].get("under_construction", "This section is under construction."))


# --- Handlers ---
start_handler = CommandHandler("start", start)
lang_handler = CallbackQueryHandler(language_select_and_register, pattern='^lang_')
# This will handle all menu buttons that don't have a specific handler yet
menu_placeholder_handler = CallbackQueryHandler(placeholder_handler, pattern='^menu_')
