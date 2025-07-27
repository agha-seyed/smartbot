import requests
from telegram import Update
from telegram.ext import (
    MessageHandler,
    ContextTypes,
    filters,
)
from studentbot.config import HUGGINGFACE_API_KEY, WHISPER_API_URL
from studentbot.utils.ai_utils import get_best_answer
from studentbot.utils.db import get_db, FAQ

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles a user's voice message, converts it to text, finds an answer,
    and sends the answer back to the user.
    """
    voice = await update.message.voice.get_file()
    voice_file = await voice.download_as_bytearray()

    if not WHISPER_API_URL or not HUGGINGFACE_API_KEY:
        await update.message.reply_text("Sorry, I can't process voice messages right now.")
        return

    try:
        response = requests.post(
            WHISPER_API_URL,
            headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
            data=voice_file,
        )
        response.raise_for_status()
        text = response.json().get("text", "")

        if text:
            db_session = next(get_db())
            faqs = db_session.query(FAQ).all()

            answer = get_best_answer(text, faqs)

            if answer:
                await update.message.reply_text(answer)
            else:
                await update.message.reply_text("I could not find an answer to your question.")
        else:
            await update.message.reply_text("I could not understand what you said.")

    except requests.exceptions.RequestException as e:
        print(f"Error calling Whisper API: {e}")
        await update.message.reply_text("Sorry, I can't process voice messages right now.")

handlers = [
    MessageHandler(filters.VOICE, handle_voice_message)
]
