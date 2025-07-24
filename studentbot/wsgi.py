import asyncio
from main import app
from config import TELEGRAM_TOKEN, BASE_URL, WEBHOOK_SECRET

async def setup():
    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=8000, # Gunicorn will manage the external port
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{BASE_URL}/{TELEGRAM_TOKEN}",
        secret_token=WEBHOOK_SECRET,
    )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    # The app object itself is the WSGI application
    # gunicorn wsgi:app
else:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
