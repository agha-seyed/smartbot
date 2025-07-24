from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from utils.db import SessionLocal, Gamification
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def add_points(user_id, points_to_add):
    db = SessionLocal()
    user_gamification = db.query(Gamification).filter(Gamification.user_id == user_id).first()
    if not user_gamification:
        user_gamification = Gamification(user_id=user_id, points=0)
        db.add(user_gamification)
    user_gamification.points += points_to_add
    db.commit()
    db.close()

async def show_profile(update: Update, context: CallbackContext):
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

    await update.message.reply_text(profile_text)

gamification_profile_handler = CommandHandler("gamification", show_profile)
