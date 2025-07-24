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
    # Placeholder handlers will be replaced as features are built
)

def main() -> None:
    """Run the bot."""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # --- Core Handlers ---
    app.add_handler(cmd_start.start_handler)
    app.add_handler(cmd_start.lang_handler)

    # --- Menu Placeholder Handlers ---
    # Handles buttons for features that are not yet implemented
    app.add_handler(cmd_start.menu_placeholder_handler)

    # --- Feature Handlers ---
    # Connect existing handlers to their new callback_data
    app.add_handler(profile_handler.profile_conv_handler) # Entry via /profile for now
    app.add_handler(isee_handler.isee_conv_handler) # Entry via /isee for now
    app.add_handler(question_handler.question_conv_handler) # Entry via /question for now
    app.add_handler(weather_handler.weather_handler) # Entry via /weather for now

    # This handler was specifically requested and is now connected to a button
    app.add_handler(apps_guide_handler.apps_guide_handler)

    # Note: Other handlers like consult, file, gamification, location, live_chat
    # are not connected to the main menu yet and will be integrated in the next steps.

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
