# بخش: Handlerهای اصلی
# فایل: audio_handler.py

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from studentbot.config import logger
from gtts import gTTS
import whisper
import os

# Load whisper model
whisper_model = whisper.load_model("base")

async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Convert text to speech and send it as a voice message.
    """
    user_id = update.effective_user.id
    text = " ".join(context.args)
    logger.info(f"User {user_id} requested text-to-speech for: {text}")

    if not text:
        await update.message.reply_text("Please provide some text to convert to speech. Usage: /tts <text>")
        return

    try:
        tts = gTTS(text=text, lang='en')
        file_path = f"temp/{user_id}.mp3"
        tts.save(file_path)

        with open(file_path, "rb") as voice:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice)

        os.remove(file_path)

    except Exception as e:
        logger.error(f"Error converting text to speech for user {user_id}: {e}")
        await update.message.reply_text("An error occurred during text-to-speech conversion.")

async def speech_to_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Convert a voice message to text.
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent a voice message for speech-to-text.")

    try:
        file = await update.message.voice.get_file()
        file_path = f"temp/{file.file_id}.ogg"
        await file.download_to_drive(file_path)

        result = whisper_model.transcribe(file_path)
        text = result["text"]

        await update.message.reply_text(f"Transcription: {text}")

        os.remove(file_path)

    except Exception as e:
        logger.error(f"Error converting speech to text for user {user_id}: {e}")
        await update.message.reply_text("An error occurred during speech-to-text conversion.")

# Define handlers for main.py
handlers = [
    CommandHandler("tts", text_to_speech),
    MessageHandler(filters.VOICE, speech_to_text),
]
