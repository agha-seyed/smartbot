import asyncio
import logging
from telegram.ext import Application
from telegram import BotCommand
from config import TELEGRAM_TOKEN, logger
from handlers import (
    start_handlers,
    profile_handlers,
    file_handlers,
    question_handlers,
    weather_handlers,
    consult_handlers,
    isee_handlers,
    gamification_handlers,
    live_chat_handlers,
    location_handlers,
    feedback_handlers,
    apps_guide_handlers,
    admin_handlers,
    search_handlers,
    menu_handlers,
    submenu_handlers,
    static_info_handlers,
    audio_handlers,
)

async def set_bot_commands(application):
    """
    Set bot commands for users.
    """
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("profile", "Create or view your profile"),
        BotCommand("search", "Search for information"),
        BotCommand("isee", "Calculate your ISEE"),
        BotCommand("consult", "Request a consultation"),
        BotCommand("upload", "Upload a file"),
        BotCommand("tts", "Convert text to speech"),
        BotCommand("progress", "View your migration progress"),
        BotCommand("deadlines", "View upcoming deadlines"),
        BotCommand("points", "View your points"),
        BotCommand("leaderboard", "View the leaderboard"),
    ]
    await application.bot.set_my_commands(commands)

async def main():
    """
    Main function to initialize and run the bot.
    """
    logger.info("Starting StudentBot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    all_handlers = (
        start_handlers +
        profile_handlers +
        file_handlers +
        question_handlers +
        weather_handlers +
        consult_handlers +
        isee_handlers +
        gamification_handlers +
        live_chat_handlers +
        location_handlers +
        feedback_handlers +
        apps_guide_handlers +
        admin_handlers +
        search_handlers +
        menu_handlers +
        submenu_handlers +
        static_info_handlers +
        audio_handlers
    )

    for handler in all_handlers:
        application.add_handler(handler)

    # Set bot commands
    await set_bot_commands(application)

    # Start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("StudentBot is running!")

    # Keep the bot running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error running bot: {e}")