# بخش: قابلیت‌های اضافی
# فایل: search_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from config import logger, ADMIN_CHAT_ID
from utils.gsheets import append_to_sheet
from utils.db import get_db, User
from utils.gamification import add_points
from sqlalchemy.orm import Session
from datetime import datetime
import json

# States for ConversationHandler
SEARCH_QUERY, SELECT_RESULT = range(2)

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

def load_apps() -> dict:
    """
    Load apps data from apps.json.
    """
    try:
        with open("apps.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Apps file apps.json not found.")
        return {"categories": []}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in apps.json.")
        return {"categories": []}

def load_scholarships() -> dict:
    """
    Load scholarships data from scholarships.json.
    """
    try:
        with open("scholarships.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Scholarships file scholarships.json not found.")
        return {"scholarships": []}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in scholarships.json.")
        return {"scholarships": []}

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the search process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} started search.")

    # Check if user has a profile
    db: Session = next(get_db())
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        await update.message.reply_text(
            texts.get("no_profile", "Please create your profile first using /profile.")
        )
        return ConversationHandler.END

    context.user_data["user_profile"] = {
        "first_name": user.first_name,
        "family_name": user.family_name,
        "age": user.age,
        "email": user.email,
        "field_of_study": user.field_of_study,
        "country": user.country
    }

    await update.message.reply_text(
        texts.get("search_prompt", "Please enter a keyword to search (e.g., Germany, language, scholarship):")
    )
    return SEARCH_QUERY

async def search_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the search query and show results.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    query = update.message.text.strip().lower()
    logger.info(f"User {user_id} searched for: {query}")

    if not query or len(query) > 100:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid search query (1-100 characters).")
        )
        return SEARCH_QUERY

    # Search in apps and scholarships
    apps_data = load_apps()
    scholarships_data = load_scholarships()
    results = []

    # Search apps
    for category in apps_data["categories"]:
        for app in category["apps"]:
            if (query in app["name"].lower() or
                query in app["description"][lang].lower() or
                query in category["display_name"][lang].lower()):
                results.append({
                    "type": "app",
                    "name": app["name"],
                    "category": category["display_name"][lang],
                    "description": app["description"][lang],
                    "link": app["link"]
                })

    # Search scholarships
    for scholarship in scholarships_data["scholarships"]:
        if (query in scholarship["name"].lower() or
            query in scholarship["description"][lang].lower() or
            query in scholarship["country"].lower() or
            query in scholarship["field"].lower()):
            results.append({
                "type": "scholarship",
                "name": scholarship["name"],
                "description": scholarship["description"][lang],
                "link": scholarship["link"],
                "country": scholarship["country"],
                "field": scholarship["field"]
            })

    if not results:
        await update.message.reply_text(
            texts.get("search_no_results", "No results found for your query.")
        )
        return SEARCH_QUERY

    context.user_data["search_results"] = results
    keyboard = [
        [InlineKeyboardButton(f"{r['type'].capitalize()}: {r['name']}", callback_data=f"result_{i}")]
        for i, r in enumerate(results)
    ]
    keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_search")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get("search_results", "Search Results:"),
        reply_markup=reply_markup
    )

    # Save search to Google Sheets
    profile = context.user_data["user_profile"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [
        user_id,
        profile["first_name"] or "",
        profile["family_name"] or "",
        profile["age"] or "",
        profile["email"] or "",
        profile["field_of_study"] or "",
        profile["country"] or "",
        f"Search: {query}",
        "",  # Empty Answer column
        timestamp
    ]
    append_to_sheet("StudentBotQuestions", data)

    # Add points for search
    db: Session = next(get_db())
    add_points(user_id, 5, db)  # Add 5 points

    return SELECT_RESULT

async def select_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle selection of a search result.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    callback_data = query.data

    if callback_data == "cancel_search":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Search cancelled.")
        )
        context.user_data.pop("user_profile", None)
        context.user_data.pop("search_results", None)
        return ConversationHandler.END

    result_index = int(callback_data.split("_")[1])
    results = context.user_data.get("search_results", [])
    if result_index < 0 or result_index >= len(results):
        await query.message.reply_text(
            texts.get("error_message", "Invalid selection. Please try again.")
        )
        return SELECT_RESULT

    result = results[result_index]
    if result["type"] == "app":
        result_details = (
            f"App: {result['name']}\n"
            f"Category: {result['category']}\n"
            f"Description: {result['description']}\n"
            f"Link: {result['link']}"
        )
    else:
        result_details = (
            f"Scholarship: {result['name']}\n"
            f"Description: {result['description']}\n"
            f"Country: {result['country']}\n"
            f"Field: {result['field']}\n"
            f"Link: {result['link']}"
        )

    await query.message.reply_text(
        texts.get("search_result_details", "Result Details:\n") + result_details
    )

    # Notify admin
    profile = context.user_data["user_profile"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    admin_message = (
        texts.get("search_admin_notify", "New search result selected:\n")
        + f"User ID: {user_id}\n"
        + f"Name: {profile['first_name']} {profile['family_name']}\n"
        + f"Age: {profile['age']}\n"
        + f"Email: {profile['email']}\n"
        + f"Field of Study: {profile['field_of_study']}\n"
        + f"Country: {profile['country']}\n"
        + f"Result: {result_details}\n"
        + f"Time: {timestamp}"
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message
    )

    context.user_data.pop("user_profile", None)
    context.user_data.pop("search_results", None)
    return ConversationHandler.END

async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel search and end the conversation.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} cancelled search.")

    await update.message.reply_text(
        texts.get("conversation_cancelled", "Search cancelled.")
    )
    context.user_data.pop("user_profile", None)
    context.user_data.pop("search_results", None)
    return ConversationHandler.END

# Define ConversationHandler
search_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("search", start_search)],
    states={
        SEARCH_QUERY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, search_query)
        ],
        SELECT_RESULT: [
            CallbackQueryHandler(select_result, pattern="^result_|^cancel_search$")
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_search)],
)

# Define handlers for main.py
handlers = [search_conv_handler]