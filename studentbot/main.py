from telegram.ext import Application
from config import TELEGRAM_TOKEN, BASE_URL, WEBHOOK_SECRET, PORT
from handlers import (
    cmd_start,
    profile_handler,
    isee_handler,
    consult_handler,
    question_handler,
    weather_handler,
    apps_guide_handler,
    menu_handler,
    search_handler,
    file_handler,
    gamification_handler,
    location_handler,
    live_chat_handler,
)

def main() -> None:
    """Run the bot."""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # --- Core Onboarding Handler ---
    app.add_handler(cmd_start.onboarding_conv_handler)

    # --- Feature Handlers ---
    app.add_handler(isee_handler.isee_conv_handler)
    app.add_handler(consult_handler.consult_conv_handler)
    app.add_handler(question_handler.question_conv_handler)
    app.add_handler(search_handler.search_handler)

    for handler in menu_handler.menu_handlers:
        app.add_handler(handler)

    app.add_handler(file_handler.file_menu_handler)
    app.add_handler(file_handler.file_sender_handler)
    app.add_handler(location_handler.location_menu_handler)
    app.add_handler(location_handler.location_sender_handler)

    app.add_handler(live_chat_handler.start_chat_handler)
    app.add_handler(live_chat_handler.end_chat_handler)
    app.add_handler(live_chat_handler.user_message_handler)
    app.add_handler(live_chat_handler.admin_message_handler)


    # Start the Bot
    app.run_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        secret_token=WEBHOOK_SECRET,
        webhook_url=f"{BASE_URL}/{WEBHOOK_SECRET}",
        url_path=WEBHOOK_SECRET,
    )

if __name__ == "__main__":
    main()
