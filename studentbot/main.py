# بخش: جریان اصلی ربات
# فایل: main.py

import logging
from telegram.ext import Application, CommandHandler
from telegram import BotCommand
from config import TELEGRAM_TOKEN, logger
from handlers.cmd_start import start
from handlers.profile_handler import handlers as profile_handlers
from handlers.file_handler import handlers as file_handlers
from handlers.question_handler import handlers as question_handlers
from handlers.weather_handler import handlers as weather_handlers
from handlers.consult_handler import handlers as consult_handlers
from handlers.isee_handler import handlers as isee_handlers
from handlers.gamification_handler import handlers as gamification_handlers
from handlers.live_chat_handler import handlers as live_chat_handlers
from handlers.location_handler import handlers as location_handlers
from handlers.feedback_handler import handlers as feedback_handlers
from handlers.apps_guide_handler import handlers as apps_guide_handlers
from handlers.search_handler import handlers as search_handlers
from handlers.admin_handler import handlers as admin_handlers

async def set_bot_commands(application):
    """
    Set bot commands for users (excluding admin commands).
    """
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("profile", "Manage your profile"),
        BotCommand("ask", "Ask a question"),
        BotCommand("consult", "Request a consultation"),
        BotCommand("weather", "Check weather"),
        BotCommand("isee", "Submit ISEE"),
        BotCommand("points", "View your points"),
        BotCommand("leaderboard", "View leaderboard"),
        BotCommand("location", "Share your location"),
        BotCommand("feedback", "Submit feedback"),
        BotCommand("apps", "Explore apps"),
        BotCommand("search", "Search scholarships and apps")
    ]
    await application.bot.set_my_commands(commands)

async def main():
    """
    Main function to run the bot.
    """
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logger.info("Starting bot...")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    for handler in profile_handlers:
        application.add_handler(handler)
    for handler in file_handlers:
        application.add_handler(handler)
    for handler in question_handlers:
        application.add_handler(handler)
    for handler in weather_handlers:
        application.add_handler(handler)
    for handler in consult_handlers:
        application.add_handler(handler)
    for handler in isee_handlers:
        application.add_handler(handler)
    for handler in gamification_handlers:
        application.add_handler(handler)
    for handler in live_chat_handlers:
        application.add_handler(handler)
    for handler in location_handlers:
        application.add_handler(handler)
    for handler in feedback_handlers:
        application.add_handler(handler)
    for handler in apps_guide_handlers:
        application.add_handler(handler)
    for handler in search_handlers:
        application.add_handler(handler)
    for handler in admin_handlers:
        application.add_handler(handler)

    # Set bot commands
    await set_bot_commands(application)

    # Start the bot
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())