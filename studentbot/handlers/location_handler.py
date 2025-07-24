from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def send_location(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    location_name = " ".join(context.args).lower() if context.args else None
    if not location_name:
        await update.message.reply_text(texts["location_name_missing"])
        return

    locations = {
        "university": {"latitude": 43.1122, "longitude": 12.3884, "title": "University of Perugia"},
        "adisu": {"latitude": 43.1073, "longitude": 12.3891, "title": "ADiSU Perugia"},
        "embassy": {"latitude": 41.9109, "longitude": 12.4818, "title": "Italian Embassy (Example)"}
    }

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
        await update.message.reply_text(texts["location_not_found"])

location_handler = CommandHandler("location", send_location)
