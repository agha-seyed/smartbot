from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from config import logger
from . import (
    profile_handler,
    isee_handler,
    consult_handler,
    question_handler,
    weather_handler,
    apps_guide_handler,
    search_handler,
    file_handler,
    gamification_handler,
    location_handler,
    live_chat_handler,
)

def feature_with_points(handler, points=5):
    """Wrapper to add points for using a feature."""
    async def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        logger.info(f"User {user_id} used feature {handler.__name__} and got {points} points.")
        gamification_handler.add_points(user_id, points)
        await handler(update, context)
    return wrapper

async def profile_button(update: Update, context: CallbackContext):
    """Handles the 'Profile' button press."""
    await profile_handler.show_profile(update, context)

async def isee_button(update: Update, context: CallbackContext):
    """Handles the 'ISEE' button press."""
    await isee_handler.start_isee_calculation(update, context)

async def consult_button(update: Update, context: CallbackContext):
    """Handles the 'Consult' button press."""
    await consult_handler.start_consult(update, context)

async def question_button(update: Update, context: CallbackContext):
    """Handles the 'Question' button press."""
    await question_handler.start_question(update, context)

async def weather_button(update: Update, context: CallbackContext):
    """Handles the 'Weather' button press."""
    await weather_handler.show_weather(update, context)

async def apps_guide_button(update: Update, context: CallbackContext):
    """Handles the 'Apps Guide' button press."""
    await apps_guide_handler.show_apps_guide(update, context)

async def search_button(update: Update, context: CallbackContext):
    """Handles the 'Search' button press."""
    await search_handler.start_search(update, context)

async def file_button(update: Update, context: CallbackContext):
    """Handles the 'File' button press."""
    await file_handler.show_file_menu(update, context)

async def gamification_button(update: Update, context: CallbackContext):
    """Handles the 'Gamification' button press."""
    await gamification_handler.show_gamification_profile(update, context)

async def location_button(update: Update, context: CallbackContext):
    """Handles the 'Location' button press."""
    await location_handler.show_location_menu(update, context)

async def live_chat_button(update: Update, context: CallbackContext):
    """Handles the 'Live Chat' button press."""
    await live_chat_handler.start_chat(update, context)

# --- Callback Query Handlers ---
menu_handlers = [
    CallbackQueryHandler(feature_with_points(profile_button), pattern='^profile$'),
    CallbackQueryHandler(feature_with_points(isee_button), pattern='^isee$'),
    CallbackQueryHandler(feature_with_points(consult_button), pattern='^consult$'),
    CallbackQueryHandler(feature_with_points(question_button), pattern='^question$'),
    CallbackQueryHandler(feature_with_points(weather_button), pattern='^weather$'),
    CallbackQueryHandler(feature_with_points(apps_guide_button), pattern='^apps_guide$'),
    CallbackQueryHandler(feature_with_points(search_button), pattern='^search$'),
    CallbackQueryHandler(feature_with_points(file_button), pattern='^file$'),
    CallbackQueryHandler(feature_with_points(gamification_button, points=0), pattern='^gamification$'), # No points for checking points
    CallbackQueryHandler(feature_with_points(location_button), pattern='^location$'),
    CallbackQueryHandler(feature_with_points(live_chat_button), pattern='^live_chat$'),
]
