from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, CallbackQueryHandler
from config import logger
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def show_apps_guide(update: Update, context: CallbackContext):
    """Shows the apps guide."""
    logger.info(f"User {update.effective_user.id} requested the apps guide.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    await query.message.reply_text(
        text=texts.get("apps_guide_text", "No apps guide available for your language."),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

apps_guide_handler = CallbackQueryHandler(show_apps_guide, pattern='^apps_guide$')
