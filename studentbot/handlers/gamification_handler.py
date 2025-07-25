from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from utils.db import SessionLocal, Gamification
from config import logger
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def add_points(user_id, points_to_add):
    logger.info(f"Adding {points_to_add} points to user {user_id}.")
    db = SessionLocal()
    user_gamification = db.query(Gamification).filter(Gamification.user_id == user_id).first()
    if not user_gamification:
        user_gamification = Gamification(user_id=user_id, points=0)
        db.add(user_gamification)
    user_gamification.points += points_to_add
    db.commit()
    db.close()

async def show_gamification_profile(update: Update, context: CallbackContext):
    """Shows the user's gamification profile."""
    logger.info(f"User {update.effective_user.id} requested gamification profile.")
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    user_id = update.effective_user.id

    db = SessionLocal()
    user_gamification = db.query(Gamification).filter(Gamification.user_id == user_id).first()
    db.close()

    if user_gamification:
        points = user_gamification.points
        badges = user_gamification.badges
        profile_text = texts["gamification_profile"].format(points=points, badges=badges)
    else:
        profile_text = texts["gamification_no_profile"]

    await query.message.reply_text(profile_text)

gamification_profile_handler = CallbackQueryHandler(show_gamification_profile, pattern='^gamification$')
