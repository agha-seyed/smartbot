# بخش: Handlerهای اصلی
# فایل: weather_handler.py

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
from config import logger, WEATHER_API_KEY
import requests
import json

# States for ConversationHandler
CITY = 0

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

async def start_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the weather query process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} requested weather.")

    keyboard = [
        [InlineKeyboardButton(texts.get("weather_perugia", "Weather in Perugia"), callback_data="weather_perugia")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("weather_prompt", "Please enter a city name or select Perugia:"),
        reply_markup=reply_markup
    )
    return CITY

async def get_weather_perugia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Fetch weather for Perugia directly.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await fetch_weather(query.message, context, "Perugia")
    return ConversationHandler.END

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's city input and fetch weather.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    city = update.message.text.strip()

    if not city or len(city) > 100:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid city name (1-100 characters).")
        )
        return CITY

    logger.info(f"User {user_id} requested weather for city: {city}")
    await fetch_weather(update.message, context, city)
    return ConversationHandler.END

async def fetch_weather(message, context: ContextTypes.DEFAULT_TYPE, city: str) -> None:
    """
    Fetch weather data from OpenWeatherMap API and send to user.

    Args:
        message: The message object to reply to.
        context: The context object for bot and user data.
        city (str): The city name to fetch weather for.
    """
    user_id = message.chat_id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_message = texts.get(
            "weather_response",
            "Weather in {city}:\nDescription: {weather}\nTemperature: {temp}°C\nHumidity: {humidity}%\nWind Speed: {wind_speed} m/s"
        ).format(city=city, weather=weather, temp=temp, humidity=humidity, wind_speed=wind_speed)

        await context.bot.send_message(
            chat_id=user_id,
            text=weather_message
        )
        logger.info(f"Weather data sent to user {user_id} for city {city}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error fetching weather for city {city}: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text=texts.get("weather_not_found", f"Could not find weather for {city}. Please try another city.")
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching weather for user {user_id}: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text=texts.get("error_message", "An error occurred. Please try again.")
        )

async def cancel_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel weather query and end the conversation.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled weather query.")

    await update.message.reply_text(
        texts.get("conversation_cancelled", "Weather query cancelled.")
    )
    return ConversationHandler.END

# Define ConversationHandler
weather_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("weather", start_weather)],
    states={
        CITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_city),
            CallbackQueryHandler(get_weather_perugia, pattern="^weather_perugia$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_weather)],
)

# Define handlers for main.py
handlers = [weather_conv_handler]
