from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from config import logger
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

locations = {
    "university": {"latitude": 43.1122, "longitude": 12.3884, "title": "University of Perugia"},
    "adisu": {"latitude": 43.1073, "longitude": 12.3891, "title": "ADiSU Perugia"},
    "embassy": {"latitude": 41.9109, "longitude": 12.4818, "title": "Italian Embassy (Example)"}
}

async def show_location_menu(update: Update, context: CallbackContext):
    """Shows the location menu."""
    logger.info(f"User {update.effective_user.id} requested the location menu.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    keyboard = []
    for location_name, location_data in locations.items():
        keyboard.append([InlineKeyboardButton(location_data['title'], callback_data=f"location_{location_name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(texts.get("location_menu_prompt", "Please select a location:"), reply_markup=reply_markup)

async def send_location(update: Update, context: CallbackContext):
    """Sends the selected location."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    location_name = query.data.split('_')[1]
    logger.info(f"User {update.effective_user.id} requested location: {location_name}")

    if location_name in locations:
        location_data = locations[location_name]
        await context.bot.send_location(
            chat_id=update.effective_chat.id,
            latitude=location_data["latitude"],
            longitude=location_data["longitude"]
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=location_data["title"]
        )
    else:
        logger.warning(f"Location not found: {location_name}")
        await query.message.reply_text(texts.get("location_not_found", "Location not found."))

location_menu_handler = CallbackQueryHandler(show_location_menu, pattern='^location$')
location_sender_handler = CallbackQueryHandler(send_location, pattern='^location_')
