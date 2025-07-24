import requests
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from config import OPENWEATHERMAP_API_KEY
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def get_weather(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    city = "Perugia"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']

        weather_text = texts["weather_report"].format(
            city=city,
            description=weather_description,
            temperature=temperature
        )
        await update.message.reply_text(weather_text)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(texts["weather_error"])

weather_handler = CommandHandler("weather", get_weather)
