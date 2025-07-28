# بخش: قابلیت‌های اضافی
# فایل: gamification_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from config import logger
from utils.db import get_db, User, MigrationProgress
from sqlalchemy.orm import Session
import json
from datetime import datetime

def load_texts(lang: str) -> dict:
    """
    Load language-specific texts from JSON files.
    """
    try:
        with open(f"lang/{lang}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Language file lang/{lang}.json not found.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in lang/{lang}.json.")
        return {}

def add_points(user_id: int, points: int, db: Session) -> None:
    """
    Add points to a user's account.
    """
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if user:
            user.points = (user.points or 0) + points
            db.commit()
            logger.info(f"Added {points} points to user {user_id}. Total points: {user.points}")
    except Exception as e:
        logger.error(f"Error adding points for user {user_id}: {e}")

async def show_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the user's current points.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    db: Session = next(get_db())
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        await update.message.reply_text(texts.get("no_profile", "Please create your profile first."))
        return

    await update.message.reply_text(texts.get("your_points", "Your points: {points}").format(points=user.points))

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the top 5 users with the highest points.
    """
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    db: Session = next(get_db())
    top_users = db.query(User).order_by(User.points.desc()).limit(5).all()

    if not top_users:
        await update.message.reply_text(texts.get("leaderboard_empty", "Leaderboard is empty."))
        return

    leaderboard_text = texts.get("leaderboard_title", "Leaderboard:") + "\n"
    for i, user in enumerate(top_users, 1):
        leaderboard_text += f"{i}. {user.first_name} - {user.points} {texts.get('points', 'points')}\n"

    await update.message.reply_text(leaderboard_text)

async def show_migration_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the user's migration progress.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    db: Session = next(get_db())
    progress = db.query(MigrationProgress).filter_by(user_id=user_id).all()

    # Define migration steps
    migration_steps = ["pre_enrollment", "visa", "arrival", "residence_permit"]

    if not progress:
        # Initialize progress for the user
        for step in migration_steps:
            new_progress = MigrationProgress(user_id=user_id, step=step)
            db.add(new_progress)
        db.commit()
        progress = db.query(MigrationProgress).filter_by(user_id=user_id).all()

    progress_text = texts.get("migration_progress_title", "Migration Progress:") + "\n"
    for step in migration_steps:
        p = next((p for p in progress if p.step == step), None)
        status = "✅" if p and p.completed else "❌"
        progress_text += f"{status} {texts.get(f'migration_step_{step}', step)}\n"

    keyboard = [
        [InlineKeyboardButton(texts.get(f"migration_step_{step}", step), callback_data=f"progress_{step}")]
        for step in migration_steps
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(progress_text, reply_markup=reply_markup)

async def toggle_progress_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Toggle the completion status of a migration progress step.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    step = query.data.split("_")[1]

    db: Session = next(get_db())
    progress_item = db.query(MigrationProgress).filter_by(user_id=user_id, step=step).first()
    if progress_item:
        progress_item.completed = not progress_item.completed
        db.commit()
        await show_migration_progress(query, context) # Show updated progress

async def show_deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show upcoming deadlines from a predefined list.
    """
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    # In a real application, this would come from a database or an external source
    deadlines = [
        {"name": "Scholarship Application", "date": "2024-09-01"},
        {"name": "Pre-enrollment", "date": "2024-08-15"},
    ]

    deadlines_text = texts.get("deadlines_title", "Upcoming Deadlines:") + "\n"
    for d in deadlines:
        deadlines_text += f"- {d['name']}: {d['date']}\n"

    await update.message.reply_text(deadlines_text)

# Define handlers for main.py
handlers = [
    CommandHandler("points", show_points),
    CommandHandler("leaderboard", show_leaderboard),
    CommandHandler("progress", show_migration_progress),
    CommandHandler("deadlines", show_deadlines),
    CallbackQueryHandler(toggle_progress_step, pattern="^progress_"),
]
