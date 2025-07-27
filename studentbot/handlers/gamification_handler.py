# بخش: قابلیت‌های اضافی
# فایل: gamification_handler.py
# بخش: قابلیت‌های اضافی
# فایل: gamification_handler.py

# فایل: handlers/gamification_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from config import logger
from utils.db import get_db, User
from sqlalchemy.orm import Session
import json

from utils.menu_utils import load_texts

def add_points(user_id: int, points: int, db: Session) -> None:
    """
    Add points to a user's account.
    Args:
        user_id (int): Telegram user ID.
        points (int): Points to add.
        db (Session): Database session.
    """
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if user:
            user.points = (user.points or 0) + points
            db.commit()
            logger.info(f"Added {points} points to user {user_id}. Total points: {user.points}")
        else:
            logger.error(f"User {user_id} not found for adding points.")
    except Exception as e:
        logger.error(f"Error adding points for user {user_id}: {e}")

async def show_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the user's current points.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} requested points.")

    try:
        db: Session = next(get_db())
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            await update.message.reply_text(
                texts.get("no_profile", "Please create your profile first using /profile.")
            )
            return

        points = user.points or 0
        await update.message.reply_text(
            texts.get("points_status", "Your current points: {points}").format(points=points)
        )
    except Exception as e:
        logger.error(f"Error showing points for user {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the top 5 users with the highest points.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} requested leaderboard.")

    try:
        db: Session = next(get_db())
        top_users = db.query(User).order_by(User.points.desc()).limit(5).all()
        if not top_users:
            await update.message.reply_text(
                texts.get("leaderboard_empty", "No users in the leaderboard yet.")
            )
            return

        leaderboard = texts.get("leaderboard_title", "Top 5 Users:\n")
        for i, user in enumerate(top_users, 1):
            leaderboard += f"{i}. {user.first_name} {user.family_name} - {user.points or 0} {texts.get('points', 'points')}\n"

        await update.message.reply_text(leaderboard)
    except Exception as e:
        logger.error(f"Error showing leaderboard for user {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

# Define handlers for main.py
handlers = [
    CommandHandler("points", show_points),
    CommandHandler("leaderboard", show_leaderboard),
]
