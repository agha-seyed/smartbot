from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from studentbot.utils.db import get_db, Feedback
from studentbot.config import ADMIN_CHAT_ID, logger

# States for ConversationHandler
GET_RATING, GET_COMMENT = range(2)

async def ask_for_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Asks the user for feedback on a specific step.
    """
    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data="feedback.positive"),
            InlineKeyboardButton("👎", callback_data="feedback.negative"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Was this step helpful?", reply_markup=reply_markup)
    return GET_RATING

async def get_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user's rating and asks for a comment.
    """
    query = update.callback_query
    await query.answer()

    rating = query.data.split('.')[1]
    context.user_data['feedback_rating'] = rating

    await query.message.reply_text("Thank you for your feedback! Would you like to add a comment?")
    return GET_COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user's comment and saves the feedback.
    """
    user = update.effective_user
    comment = update.message.text
    rating = context.user_data.get('feedback_rating')
    step_id = context.user_data.get('current_guide_step_id', 'unknown') # Assuming this is set in the guide_handler

    db_session = next(get_db())
    new_feedback = Feedback(
        user_id=user.id,
        step_id=step_id,
        rating=rating,
        comment=comment,
        timestamp=datetime.now().isoformat()
    )
    db_session.add(new_feedback)
    db_session.commit()

    # Notify admin
    admin_message = (
        f"New Feedback from {user.full_name} (ID: {user.id}) for step {step_id}:\n\n"
        f"Rating: {rating}\n"
        f"Comment: {comment}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    await update.message.reply_text("Thank you for your valuable feedback!")

    return ConversationHandler.END

async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the case where the user skips adding a comment.
    """
    user = update.effective_user
    rating = context.user_data.get('feedback_rating')
    step_id = context.user_data.get('current_guide_step_id', 'unknown')

    db_session = next(get_db())
    new_feedback = Feedback(
        user_id=user.id,
        step_id=step_id,
        rating=rating,
        comment=None,
        timestamp=datetime.now().isoformat()
    )
    db_session.add(new_feedback)
    db_session.commit()

    # Notify admin
    admin_message = (
        f"New Feedback from {user.full_name} (ID: {user.id}) for step {step_id}:\n\n"
        f"Rating: {rating}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    await update.callback_query.message.reply_text("Thank you for your valuable feedback!")

    return ConversationHandler.END


feedback_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(ask_for_feedback, pattern="^feedback\..*")],
    states={
        GET_RATING: [CallbackQueryHandler(get_rating, pattern="^feedback\..*")],
        GET_COMMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment),
            CallbackQueryHandler(skip_comment, pattern="^skip_comment$")
        ],
    },
    fallbacks=[],
)

handlers = [feedback_conv_handler]
