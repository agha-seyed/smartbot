from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from studentbot.utils.ai_utils import get_best_answer
from studentbot.utils.db import get_db, FAQ
from studentbot.config import ADMIN_CHAT_ID, logger

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles a user's question, tries to find an answer in the FAQs,
    and forwards the question to the admin if no answer is found.
    """
    question = update.message.text
    user = update.effective_user

    db_session = next(get_db())
    faqs = db_session.query(FAQ).all()

    answer = get_best_answer(question, faqs)

    if answer:
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("I could not find an answer to your question. I will forward it to an admin.")

        admin_message = (
            f"New Question from {user.full_name} (ID: {user.id}):\n\n"
            f"{question}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

handlers = [
    MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question)
]
