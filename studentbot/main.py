# بخش: جریان اصلی ربات
# فایل: main.py

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
from config import BOT_TOKEN, BASE_URL, WEBHOOK_SECRET, PORT, logger
import os
import importlib
import glob

def load_handlers():
    """
    Dynamically load all handler modules from the handlers directory.

    Returns:
        list: List of handler objects to be registered.
    """
    handlers = []
    handlers_dir = os.path.join(os.path.dirname(__file__), "handlers")
    for handler_file in glob.glob(os.path.join(handlers_dir, "*.py")):
        if handler_file.endswith("__init__.py"):
            continue
        module_name = os.path.basename(handler_file)[:-3]  # Remove .py
        try:
            module = importlib.import_module(f"handlers.{module_name}")
            # Assume each handler module defines a list or single handler object
            if hasattr(module, "handlers"):
                handlers.extend(module.handlers if isinstance(module.handlers, list) else [module.handlers])
            elif hasattr(module, "handler"):
                handlers.append(module.handler)
            logger.info(f"Loaded handler module: {module_name}")
        except ImportError as e:
            logger.error(f"Error loading handler module {module_name}: {e}")
    return handlers

async def error_handler(update, context):
    """Handle errors that occur during update processing."""
    logger.error(f"Update {update} caused error: {context.error}")
    if update and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred. Please try again later."
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

def main():
    """Initialize and run the Telegram bot with webhook."""
    try:
        # Initialize Application
        app = Application.builder().token(BOT_TOKEN).build()

        # Load and register handlers
        handlers = load_handlers()
        for handler in handlers:
            app.add_handler(handler)
            logger.info(f"Registered handler: {handler}")

        # Add error handler
        app.add_error_handler(error_handler)

        # Set up webhook
        webhook_url = f"{BASE_URL}/{WEBHOOK_SECRET}"
        logger.info(f"Setting webhook to {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            secret_token=WEBHOOK_SECRET,
            webhook_url=webhook_url
        )
        logger.info(f"Bot is running on port {PORT}")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    main()
