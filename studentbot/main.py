# فایل: main.py

import asyncio
import logging
from telegram.ext import Application
from telegram import BotCommand
from config import TELEGRAM_TOKEN, logger
from handlers.cmd_start import handlers as start_handlers
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
from handlers.admin_handler import handlers as admin_handlers
from handlers.search_handler import handlers as search_handlers
from handlers.menu_handler import handlers as menu_handlers
from handlers.submenu_handler import handlers as submenu_handlers
from handlers.voice_handler import handlers as voice_handlers

async def set_bot_commands(application):
    """
    Set bot commands for users, excluding /admin and /login for non-admins.
    """
    commands = [
        BotCommand("start", "شروع ربات"),
        BotCommand("menu", "نمایش منوی اصلی"),
        BotCommand("profile", "مدیریت پروفایل"),
        BotCommand("ask", "پرسیدن سؤالم"),
        BotCommand("consult", "درخواست مشاوره"),
        BotCommand("weather", "بررسی آب‌وهوا"),
        BotCommand("isee", "ارسال ISEE"),
        BotCommand("points", "مشاهده امتیازات"),
        BotCommand("leaderboard", "مشاهده جدول امتیازات"),
        BotCommand("location", "اشتراک‌گذاری موقعیت مکانی"),
        BotCommand("feedback", "ارسال بازخورد"),
        BotCommand("apps", "کاوش اپلیکیشن‌ها"),
        BotCommand("search", "جستجوی بورسیه‌ها و اپلیکیشن‌ها"),
        BotCommand("guide", "راهنمای گام به گام")
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
        voice_handlers
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