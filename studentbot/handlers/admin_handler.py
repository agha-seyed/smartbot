# بخش: قابلیت‌های اضافی
# فایل: handlers/admin_handler.py

# فایل: handlers/admin_handler.py

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
from utils.gsheets import read_sheet, update_sheet, append_to_sheet
from utils.db import get_db, User, Admin
from studentbot.utils.update_from_sheets import sync_scholarships_from_sheet, sync_faqs_from_sheet
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os
import bcrypt

# States for ConversationHandler
LOGIN_USERNAME, LOGIN_PASSWORD, ADMIN_MENU, ANSWER_QUESTION, ANSWER_TEXT, BROADCAST_MESSAGE, MANAGE_SCHOLARSHIPS, ADD_SCHOLARSHIP_NAME, ADD_SCHOLARSHIP_DESC_EN, ADD_SCHOLARSHIP_DESC_FA, ADD_SCHOLARSHIP_DESC_IT, ADD_SCHOLARSHIP_LINK, ADD_SCHOLARSHIP_COUNTRY, ADD_SCHOLARSHIP_FIELD, DELETE_SCHOLARSHIP, MANAGE_USER, MANAGE_USER_ACTION = range(17)

from utils.menu_utils import load_texts

def load_scholarships() -> dict:
    """
    Load scholarships data from scholarships.json.
    """
    try:
        with open("data/scholarships.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Scholarships file data/scholarships.json not found.")
        return {"scholarships": []}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in data/scholarships.json.")
        return {"scholarships": []}

def save_scholarships(data: dict) -> None:
    """
    Save scholarships data to scholarships.json.
    """
    try:
        with open("data/scholarships.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving data/scholarships.json: {e}")

async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the admin login process.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} attempted to login as admin.")

    await update.message.reply_text(
        texts.get("admin_login_username", "Please enter your admin username:")
    )
    return LOGIN_USERNAME

async def login_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle admin username input.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    username = update.message.text.strip()
    logger.info(f"User {user_id} entered username: {username}")

    if not username or len(username) > 50:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid username (1-50 characters).")
        )
        return LOGIN_USERNAME

    context.user_data["admin_username"] = username
    await update.message.reply_text(
        texts.get("admin_login_password", "Please enter your admin password:")
    )
    return LOGIN_PASSWORD

async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle admin password input and authenticate.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    password = update.message.text.strip()
    logger.info(f"User {user_id} attempted login with username: {context.user_data['admin_username']}")

    try:
        db: Session = next(get_db())
        admin = db.query(Admin).filter_by(username=context.user_data["admin_username"]).first()
        if admin and admin.check_password(password):
            context.user_data["is_admin"] = True
            keyboard = [
                [InlineKeyboardButton(texts.get("admin_stats", "View Statistics"), callback_data="admin_stats")],
                [InlineKeyboardButton(texts.get("admin_answer", "Answer Questions"), callback_data="admin_answer")],
                [InlineKeyboardButton(texts.get("admin_broadcast", "Send Broadcast Message"), callback_data="admin_broadcast")],
                [InlineKeyboardButton(texts.get("admin_manage_scholarships", "Manage Scholarships"), callback_data="admin_manage_scholarships")],
                [InlineKeyboardButton(texts.get("admin_manage_users", "Manage Users"), callback_data="admin_manage_users")],
                [InlineKeyboardButton(texts.get("admin_logs", "View Logs"), callback_data="admin_logs")],
                [InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                texts.get("admin_menu", "Welcome to the Admin Panel. Please select an option:"),
                reply_markup=reply_markup
            )
            return ADMIN_MENU
        else:
            await update.message.reply_text(
                texts.get("admin_login_failed", "Invalid username or password.")
            )
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error during admin login for user {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )
        return ConversationHandler.END

async def start_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Check if user is already logged in as admin.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"User {user_id} attempted to access admin panel.")

    if context.user_data.get("is_admin", False):
        keyboard = [
            [InlineKeyboardButton(texts.get("admin_stats", "View Statistics"), callback_data="admin_stats")],
            [InlineKeyboardButton(texts.get("admin_answer", "Answer Questions"), callback_data="admin_answer")],
            [InlineKeyboardButton(texts.get("admin_broadcast", "Send Broadcast Message"), callback_data="admin_broadcast")],
            [InlineKeyboardButton(texts.get("admin_manage_scholarships", "Manage Scholarships"), callback_data="admin_manage_scholarships")],
            [InlineKeyboardButton(texts.get("admin_manage_users", "Manage Users"), callback_data="admin_manage_users")],
            [InlineKeyboardButton(texts.get("admin_logs", "View Logs"), callback_data="admin_logs")],
            [InlineKeyboardButton(texts.get("admin_sync", "Sync from Sheets"), callback_data="admin_sync")],
            [InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            texts.get("admin_menu", "Welcome to the Admin Panel. Please select an option:"),
            reply_markup=reply_markup
        )
        return ADMIN_MENU
    else:
        await update.message.reply_text(
            texts.get("admin_access_denied", "Please login using /login first.")
        )
        return ConversationHandler.END

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle admin menu options.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    option = query.data
    logger.info(f"Admin {user_id} selected option: {option}")

    if option == "cancel_admin":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Admin panel cancelled.")
        )
        context.user_data.pop("is_admin", None)
        context.user_data.pop("admin_username", None)
        return ConversationHandler.END

    if option == "admin_sync":
        await query.message.reply_text("Starting sync process...")
        db: Session = next(get_db())

        logger.info("Syncing scholarships...")
        scholarship_summary = sync_scholarships_from_sheet(db)
        logger.info(f"Scholarship sync summary: {scholarship_summary}")

        logger.info("Syncing FAQs...")
        faq_summary = sync_faqs_from_sheet(db)
        logger.info(f"FAQ sync summary: {faq_summary}")

        summary_message = f"Sync process finished.\n\nScholarships:\n{scholarship_summary}\n\nFAQs:\n{faq_summary}"
        await query.message.reply_text(summary_message)

        # Also send to admin chat for logging purposes
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary_message)

        return ADMIN_MENU

    if option == "admin_stats":
        try:
            db: Session = next(get_db())
            total_users = db.query(User).count()
            total_questions = len([row for row in read_sheet("StudentBotQuestions")[1:] if row[7].startswith("Question:")])
            total_feedback = len([row for row in read_sheet("StudentBotQuestions")[1:] if row[7].startswith("Rating:") or row[7].startswith("Feedback:")])
            top_users = db.query(User).order_by(User.points.desc()).limit(5).all()
            stats_message = (
                texts.get("admin_stats_title", "Statistics:\n")
                + f"Total Users: {total_users}\n"
                + f"Total Questions: {total_questions}\n"
                + f"Total Feedback: {total_feedback}\n\n"
                + texts.get("leaderboard_title", "Top 5 Users:\n")
            )
            for i, user in enumerate(top_users, 1):
                stats_message += f"{i}. {user.first_name} {user.family_name} - {user.points or 0} {texts.get('points', 'points')}\n"
            await query.message.reply_text(stats_message)
            return ADMIN_MENU
        except Exception as e:
            logger.error(f"Error showing stats for admin {user_id}: {e}")
            await query.message.reply_text(
                texts.get("error_message", "An error occurred. Please try again.")
            )
            return ADMIN_MENU

    if option == "admin_broadcast":
        await query.message.reply_text(
            texts.get("admin_broadcast_prompt", "Please enter the broadcast message:")
        )
        return BROADCAST_MESSAGE

    if option == "admin_manage_scholarships":
        scholarships = load_scholarships()
        keyboard = [
            [InlineKeyboardButton(texts.get("admin_add_scholarship", "Add Scholarship"), callback_data="add_scholarship")],
            [InlineKeyboardButton(texts.get("admin_delete_scholarship", "Delete Scholarship"), callback_data="delete_scholarship")]
        ]
        if scholarships["scholarships"]:
            for scholarship in scholarships["scholarships"]:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{scholarship['name']} (ID: {scholarship['id']})",
                        callback_data=f"view_scholarship_{scholarship['id']}"
                    )
                ])
        keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_admin")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            texts.get("admin_manage_scholarships_prompt", "Manage Scholarships:"),
            reply_markup=reply_markup
        )
        return MANAGE_SCHOLARSHIPS

    if option == "admin_manage_users":
        try:
            db: Session = next(get_db())
            users = db.query(User).limit(5).all()  # Limit to 5 for simplicity
            if not users:
                await query.message.reply_text(
                    texts.get("admin_no_users", "No users found.")
                )
                return ADMIN_MENU
            keyboard = [
                [InlineKeyboardButton(
                    f"{user.first_name} {user.family_name} (ID: {user.user_id})",
                    callback_data=f"manage_user_{user.user_id}"
                )]
                for user in users
            ]
            keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_admin")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                texts.get("admin_manage_users_prompt", "Select a user to manage:"),
                reply_markup=reply_markup
            )
            return MANAGE_USER
        except Exception as e:
            logger.error(f"Error showing users for admin {user_id}: {e}")
            await query.message.reply_text(
                texts.get("error_message", "An error occurred. Please try again.")
            )
            return ADMIN_MENU

    if option == "admin_logs":
        try:
            if os.path.exists("studentbot.log"):
                with open("studentbot.log", "r", encoding="utf-8") as f:
                    logs = f.readlines()[-10:]  # Show last 10 log lines
                log_message = texts.get("admin_logs_title", "Recent Logs:\n") + "".join(logs)
            else:
                log_message = texts.get("admin_no_logs", "No logs found.")
            await query.message.reply_text(log_message)
            return ADMIN_MENU
        except Exception as e:
            logger.error(f"Error showing logs for admin {user_id}: {e}")
            await query.message.reply_text(
                texts.get("error_message", "An error occurred. Please try again.")
            )
            return ADMIN_MENU

    if option == "admin_answer":
        try:
            sheet_data = read_sheet("StudentBotQuestions")
            unanswered = [
                row for row in sheet_data[1:]  # Skip header
                if row[8] == "" and row[7] != ""  # Empty Answer, non-empty Question/Field/Income
            ]
            if not unanswered:
                await query.message.reply_text(
                    texts.get("admin_no_unanswered", "No unanswered questions or feedback found.")
                )
                return ADMIN_MENU

            keyboard = [
                [InlineKeyboardButton(
                    f"User {row[0]}: {row[7][:30]}...",
                    callback_data=f"answer_{sheet_data.index(row)}"
                )]
                for row in unanswered[:5]  # Limit to 5 for simplicity
            ]
            keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_admin")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                texts.get("admin_answer_select", "Select an entry to answer:"),
                reply_markup=reply_markup
            )
            return ANSWER_QUESTION
        except Exception as e:
            logger.error(f"Error loading unanswered entries for admin {user_id}: {e}")
            await query.message.reply_text(
                texts.get("error_message", "An error occurred. Please try again.")
            )
            return ADMIN_MENU

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle broadcast message input and send to all users.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    message = update.message.text.strip()
    logger.info(f"Admin {user_id} submitted broadcast message: {message}")

    if not message or len(message) > 1000:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid message (1-1000 characters).")
        )
        return BROADCAST_MESSAGE

    try:
        db: Session = next(get_db())
        users = db.query(User).all()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for user in users:
            await context.bot.send_message(
                chat_id=user.user_id,
                text=texts.get("admin_broadcast_message", "Admin Broadcast: {message}").format(message=message)
            )
            data = [
                user.user_id,
                user.first_name or "",
                user.family_name or "",
                user.age or "",
                user.email or "",
                user.field_of_study or "",
                user.country or "",
                f"Broadcast: {message}",
                "",  # Empty Answer column
                timestamp
            ]
            append_to_sheet("StudentBotQuestions", data)

        await update.message.reply_text(
            texts.get("admin_broadcast_sent", "Broadcast message sent to all users.")
        )
        return ADMIN_MENU
    except Exception as e:
        logger.error(f"Error sending broadcast for admin {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )
        return BROADCAST_MESSAGE

async def manage_scholarships(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship management actions.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    action = query.data
    logger.info(f"Admin {user_id} selected scholarship action: {action}")

    if action == "cancel_admin":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Admin panel cancelled.")
        )
        return ConversationHandler.END

    if action == "add_scholarship":
        await query.message.reply_text(
            texts.get("admin_add_scholarship_name", "Please enter the scholarship name:")
        )
        return ADD_SCHOLARSHIP_NAME

    if action == "delete_scholarship":
        scholarships = load_scholarships()
        if not scholarships["scholarships"]:
            await query.message.reply_text(
                texts.get("admin_no_scholarships", "No scholarships found.")
            )
            return MANAGE_SCHOLARSHIPS
        keyboard = [
            [InlineKeyboardButton(
                f"{s['name']} (ID: {s['id']})",
                callback_data=f"delete_scholarship_{s['id']}"
            )]
            for s in scholarships["scholarships"]
        ]
        keyboard.append([InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_admin")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            texts.get("admin_delete_scholarship_prompt", "Select a scholarship to delete:"),
            reply_markup=reply_markup
        )
        return DELETE_SCHOLARSHIP

    if action.startswith("view_scholarship_"):
        scholarship_id = int(action.split("_")[2])
        scholarships = load_scholarships()
        scholarship = next((s for s in scholarships["scholarships"] if s["id"] == scholarship_id), None)
        if not scholarship:
            await query.message.reply_text(
                texts.get("error_message", "Invalid scholarship. Please try again.")
            )
            return MANAGE_SCHOLARSHIPS
        scholarship_details = (
            f"Name: {scholarship['name']}\n"
            f"Description (EN): {scholarship['description']['en']}\n"
            f"Description (FA): {scholarship['description']['fa']}\n"
            f"Description (IT): {scholarship['description']['it']}\n"
            f"Link: {scholarship['link']}\n"
            f"Country: {scholarship['country']}\n"
            f"Field: {scholarship['field']}"
        )
        await query.message.reply_text(
            texts.get("admin_scholarship_details", "Scholarship Details:\n") + scholarship_details
        )
        return MANAGE_SCHOLARSHIPS

    return MANAGE_SCHOLARSHIPS

async def add_scholarship_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship name input.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    name = update.message.text.strip()
    logger.info(f"Admin {user_id} entered scholarship name: {name}")

    if not name or len(name) > 100:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid scholarship name (1-100 characters).")
        )
        return ADD_SCHOLARSHIP_NAME

    context.user_data["new_scholarship"] = {"name": name, "description": {}}
    await update.message.reply_text(
        texts.get("admin_add_scholarship_desc_en", "Please enter the scholarship description in English:")
    )
    return ADD_SCHOLARSHIP_DESC_EN

async def add_scholarship_desc_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship description (English).
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    desc = update.message.text.strip()
    logger.info(f"Admin {user_id} entered scholarship description (EN): {desc}")

    if not desc or len(desc) > 500:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid description (1-500 characters).")
        )
        return ADD_SCHOLARSHIP_DESC_EN

    context.user_data["new_scholarship"]["description"]["en"] = desc
    await update.message.reply_text(
        texts.get("admin_add_scholarship_desc_fa", "Please enter the scholarship description in Persian:")
    )
    return ADD_SCHOLARSHIP_DESC_FA

async def add_scholarship_desc_fa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship description (Persian).
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    desc = update.message.text.strip()
    logger.info(f"Admin {user_id} entered scholarship description (FA): {desc}")

    if not desc or len(desc) > 500:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid description (1-500 characters).")
        )
        return ADD_SCHOLARSHIP_DESC_FA

    context.user_data["new_scholarship"]["description"]["fa"] = desc
    await update.message.reply_text(
        texts.get("admin_add_scholarship_desc_it", "Please enter the scholarship description in Italian:")
    )
    return ADD_SCHOLARSHIP_DESC_IT

async def add_scholarship_desc_it(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship description (Italian).
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    desc = update.message.text.strip()
    logger.info(f"Admin {user_id} entered scholarship description (IT): {desc}")

    if not desc or len(desc) > 500:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid description (1-500 characters).")
        )
        return ADD_SCHOLARSHIP_DESC_IT

    context.user_data["new_scholarship"]["description"]["it"] = desc
    await update.message.reply_text(
        texts.get("admin_add_scholarship_link", "Please enter the scholarship link:")
    )
    return ADD_SCHOLARSHIP_LINK

async def add_scholarship_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship link input.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    link = update.message.text.strip()
    logger.info(f"Admin {user_id} entered scholarship link: {link}")

    if not link or len(link) > 200:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid link (1-200 characters).")
        )
        return ADD_SCHOLARSHIP_LINK

    context.user_data["new_scholarship"]["link"] = link
    await update.message.reply_text(
        texts.get("admin_add_scholarship_country", "Please enter the scholarship country:")
    )
    return ADD_SCHOLARSHIP_COUNTRY

async def add_scholarship_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship country input.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    country = update.message.text.strip()
    logger.info(f"Admin {user_id} entered scholarship country: {country}")

    if not country or len(country) > 100:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid country (1-100 characters).")
        )
        return ADD_SCHOLARSHIP_COUNTRY

    context.user_data["new_scholarship"]["country"] = country
    await update.message.reply_text(
        texts.get("admin_add_scholarship_field", "Please enter the scholarship field (e.g., All Fields, Computer Science):")
    )
    return ADD_SCHOLARSHIP_FIELD

async def add_scholarship_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship field input and save the scholarship.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    field = update.message.text.strip()
    logger.info(f"Admin {user_id} entered scholarship field: {field}")

    if not field or len(field) > 100:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid field (1-100 characters).")
        )
        return ADD_SCHOLARSHIP_FIELD

    try:
        scholarships = load_scholarships()
        new_id = max([s["id"] for s in scholarships["scholarships"]], default=0) + 1
        new_scholarship = context.user_data["new_scholarship"]
        new_scholarship["id"] = new_id
        new_scholarship["field"] = field
        scholarships["scholarships"].append(new_scholarship)
        save_scholarships(scholarships)

        await update.message.reply_text(
            texts.get("admin_scholarship_added", "Scholarship added successfully!")
        )
        context.user_data.pop("new_scholarship", None)
        return MANAGE_SCHOLARSHIPS
    except Exception as e:
        logger.error(f"Error adding scholarship for admin {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )
        return ADD_SCHOLARSHIP_FIELD

async def delete_scholarship(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle scholarship deletion.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    action = query.data

    if action == "cancel_admin":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Admin panel cancelled.")
        )
        return ConversationHandler.END

    scholarship_id = int(action.split("_")[2])
    try:
        scholarships = load_scholarships()
        scholarships["scholarships"] = [s for s in scholarships["scholarships"] if s["id"] != scholarship_id]
        save_scholarships(scholarships)
        await query.message.reply_text(
            texts.get("admin_scholarship_deleted", "Scholarship deleted successfully!")
        )
        return MANAGE_SCHOLARSHIPS
    except Exception as e:
        logger.error(f"Error deleting scholarship {scholarship_id} for admin {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )
        return MANAGE_SCHOLARSHIPS

async def manage_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user management selection.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    action = query.data

    if action == "cancel_admin":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Admin panel cancelled.")
        )
        return ConversationHandler.END

    target_user_id = int(action.split("_")[2])
    context.user_data["target_user_id"] = target_user_id
    logger.info(f"Admin {user_id} selected user {target_user_id} to manage.")

    try:
        db: Session = next(get_db())
        user = db.query(User).filter_by(user_id=target_user_id).first()
        if not user:
            await query.message.reply_text(
                texts.get("admin_no_user", "User not found.")
            )
            return MANAGE_USER

        user_details = (
            f"User ID: {user.user_id}\n"
            f"Name: {user.first_name} {user.family_name}\n"
            f"Age: {user.age}\n"
            f"Email: {user.email}\n"
            f"Field of Study: {user.field_of_study}\n"
            f"Country: {user.country}\n"
            f"Points: {user.points or 0}"
        )
        keyboard = [
            [InlineKeyboardButton(texts.get("admin_change_points", "Change Points"), callback_data="change_points")],
            [InlineKeyboardButton(texts.get("cancel", "Cancel"), callback_data="cancel_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            texts.get("admin_manage_user_prompt", "User Details:\n") + user_details,
            reply_markup=reply_markup
        )
        return MANAGE_USER_ACTION
    except Exception as e:
        logger.error(f"Error showing user {target_user_id} for admin {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )
        return MANAGE_USER

async def manage_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user management actions.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    action = query.data

    if action == "cancel_admin":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Admin panel cancelled.")
        )
        context.user_data.pop("target_user_id", None)
        return ConversationHandler.END

    if action == "change_points":
        await query.message.reply_text(
            texts.get("admin_change_points_prompt", "Please enter the new points value (positive or negative):")
        )
        return MANAGE_USER_ACTION

async def change_user_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle changing user points.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    target_user_id = context.user_data.get("target_user_id")
    try:
        points = int(update.message.text.strip())
        logger.info(f"Admin {user_id} changing points for user {target_user_id} to {points}")

        db: Session = next(get_db())
        user = db.query(User).filter_by(user_id=target_user_id).first()
        if not user:
            await update.message.reply_text(
                texts.get("admin_no_user", "User not found.")
            )
            return MANAGE_USER

        user.points = (user.points or 0) + points
        db.commit()
        await update.message.reply_text(
            texts.get("admin_points_updated", "User points updated successfully. New points: {points}").format(points=user.points)
        )
        context.user_data.pop("target_user_id", None)
        return ADMIN_MENU
    except ValueError:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid number for points.")
        )
        return MANAGE_USER_ACTION
    except Exception as e:
        logger.error(f"Error changing points for user {target_user_id} by admin {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )
        return MANAGE_USER_ACTION

async def select_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle selection of an entry to answer.
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    callback_data = query.data

    if callback_data == "cancel_admin":
        await query.message.reply_text(
            texts.get("conversation_cancelled", "Admin panel cancelled.")
        )
        return ConversationHandler.END

    row_index = int(callback_data.split("_")[1])
    context.user_data["answer_row_index"] = row_index
    logger.info(f"Admin {user_id} selected entry {row_index} to answer.")

    try:
        sheet_data = read_sheet("StudentBotQuestions")
        if row_index < 1 or row_index >= len(sheet_data):
            await query.message.reply_text(
                texts.get("error_message", "Invalid entry selected. Please try again.")
            )
            return ANSWER_QUESTION

        entry = sheet_data[row_index]
        entry_details = (
            f"User ID: {entry[0]}\n"
            f"Name: {entry[1]} {entry[2]}\n"
            f"Age: {entry[3]}\n"
            f"Email: {entry[4]}\n"
            f"Field of Study: {entry[5]}\n"
            f"Country: {entry[6]}\n"
            f"Question/Feedback: {entry[7]}\n"
            f"Time: {entry[9]}"
        )
        await query.message.reply_text(
            texts.get("admin_answer_prompt", "Please provide your answer for the following entry:\n\n") + entry_details
        )
        return ANSWER_TEXT
    except Exception as e:
        logger.error(f"Error showing entry {row_index} for admin {user_id}: {e}")
        await query.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )
        return ANSWER_QUESTION

async def submit_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the admin's answer to Google Sheets and notify the user.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    answer_text = update.message.text.strip()
    row_index = context.user_data.get("answer_row_index")
    logger.info(f"Admin {user_id} submitted answer for entry {row_index}: {answer_text}")

    if not answer_text or len(answer_text) > 1000:
        await update.message.reply_text(
            texts.get("error_message", "Please enter a valid answer (1-1000 characters).")
        )
        return ANSWER_TEXT

    try:
        sheet_data = read_sheet("StudentBotQuestions")
        if row_index < 1 or row_index >= len(sheet_data):
            await update.message.reply_text(
                texts.get("error_message", "Invalid entry. Please try again.")
            )
            return ANSWER_QUESTION

        entry = sheet_data[row_index]
        target_user_id = int(entry[0])
        update_sheet("StudentBotQuestions", row_index + 1, 9, answer_text)

        await context.bot.send_message(
            chat_id=target_user_id,
            text=texts.get("admin_response", "Admin response: {answer}").format(answer=answer_text)
        )

        await update.message.reply_text(
            texts.get("admin_answer_submitted", "Your answer has been submitted and the user has been notified.")
        )
    except Exception as e:
        logger.error(f"Error submitting answer for entry {row_index} by admin {user_id}: {e}")
        await update.message.reply_text(
            texts.get("error_message", "An error occurred. Please try again.")
        )

    context.user_data.pop("answer_row_index", None)
    return ADMIN_MENU

async def cancel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel admin actions and end the conversation.
    """
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    logger.info(f"Admin {user_id} cancelled admin panel.")

    await update.message.reply_text(
        texts.get("conversation_cancelled", "Admin panel cancelled.")
    )
    context.user_data.pop("answer_row_index", None)
    context.user_data.pop("new_scholarship", None)
    context.user_data.pop("target_user_id", None)
    context.user_data.pop("admin_username", None)
    context.user_data.pop("is_admin", None)
    return ConversationHandler.END

# Define ConversationHandler
admin_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("admin", start_admin),
        CommandHandler("login", start_login)
    ],
    states={
        LOGIN_USERNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)
        ],
        LOGIN_PASSWORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)
        ],
        ADMIN_MENU: [
            CallbackQueryHandler(admin_menu, pattern="^admin_stats|^admin_answer|^admin_broadcast|^admin_manage_scholarships|^admin_manage_users|^admin_logs|^admin_sync|^cancel_admin$")
        ],
        ANSWER_QUESTION: [
            CallbackQueryHandler(select_answer, pattern="^answer_|^cancel_admin$")
        ],
        ANSWER_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, submit_answer)
        ],
        BROADCAST_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)
        ],
        MANAGE_SCHOLARSHIPS: [
            CallbackQueryHandler(manage_scholarships, pattern="^add_scholarship|^delete_scholarship|^view_scholarship_|^cancel_admin$")
        ],
        ADD_SCHOLARSHIP_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_scholarship_name)
        ],
        ADD_SCHOLARSHIP_DESC_EN: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_scholarship_desc_en)
        ],
        ADD_SCHOLARSHIP_DESC_FA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_scholarship_desc_fa)
        ],
        ADD_SCHOLARSHIP_DESC_IT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_scholarship_desc_it)
        ],
        ADD_SCHOLARSHIP_LINK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_scholarship_link)
        ],
        ADD_SCHOLARSHIP_COUNTRY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_scholarship_country)
        ],
        ADD_SCHOLARSHIP_FIELD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_scholarship_field)
        ],
        DELETE_SCHOLARSHIP: [
            CallbackQueryHandler(delete_scholarship, pattern="^delete_scholarship_|^cancel_admin$")
        ],
        MANAGE_USER: [
            CallbackQueryHandler(manage_user, pattern="^manage_user_|^cancel_admin$")
        ],
        MANAGE_USER_ACTION: [
            CallbackQueryHandler(manage_user_action, pattern="^change_points|^cancel_admin$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, change_user_points)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_admin)],
)

# Define handlers for main.py
handlers = [admin_conv_handler]
