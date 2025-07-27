import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)
from studentbot.config import logger
from studentbot.utils.menu_utils import load_texts
from studentbot.utils.lang import language_decorator

# States for ConversationHandler
GUIDE_STEP = 0

def load_knowledge_base():
    """
    Loads the knowledge base from the knowledge.json file.
    """
    try:
        with open('studentbot/config/knowledge.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading knowledge base: {e}")
        return {}

@language_decorator
async def start_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the step-by-step guide.
    """
    context.user_data['guide_step'] = 0
    await show_guide_step(update, context)
    return GUIDE_STEP

async def show_guide_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays the current step of the guide.
    """
    user_lang = context.user_data.get("lang", "fa")
    knowledge_base = load_knowledge_base().get("guide", {}).get(user_lang, {})
    steps = knowledge_base.get("steps", [])
    step_index = context.user_data.get('guide_step', 0)

    if not steps or not (0 <= step_index < len(steps)):
        await update.message.reply_text("Guide not available.")
        return

    step = steps[step_index]
    title = step.get("title", "")
    content = step.get("content", "")

    # Add country-specific tip if available
    user_country = context.user_data.get("country")
    if user_country and "tips" in step and user_country in step["tips"]:
        tip = step["tips"][user_country]
        content += f"\n\n*Tip for students from {user_country}:* {tip}"

    keyboard = []
    row = []
    texts = load_texts(user_lang)
    if step_index > 0:
        row.append(InlineKeyboardButton(texts.get("prev_step", "⬅️ Previous"), callback_data="guide.prev"))
    if step_index < len(steps) - 1:
        row.append(InlineKeyboardButton(texts.get("next_step", "Next ➡️"), callback_data="guide.next"))
    keyboard.append(row)
    keyboard.append([InlineKeyboardButton(texts.get("back_to_menu", "⏹️ Back to Menu"), callback_data="guide.menu")])

    # Add feedback buttons
    feedback_keyboard = [
        InlineKeyboardButton("👍 Helpful", callback_data=f"feedback.positive.{step_index}"),
        InlineKeyboardButton("👎 Not Helpful", callback_data=f"feedback.negative.{step_index}")
    ]
    keyboard.append(feedback_keyboard)

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = f"*{title}*\n\n{content}"

    if update.callback_query:
        await update.callback_query.message.edit_text(message_text, reply_markup=reply_markup, parse_mode="MarkdownV2")
    else:
        await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode="MarkdownV2")

async def guide_navigation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles navigation within the guide.
    """
    query = update.callback_query
    await query.answer()

    action = query.data.split('.')[1]
    step_index = context.user_data.get('guide_step', 0)

    if action == "next":
        step_index += 1
    elif action == "prev":
        step_index -= 1
    elif action == "menu":
        from studentbot.handlers.menu_handler import show_dynamic_menu
        await show_dynamic_menu(update, context)
        return ConversationHandler.END

    context.user_data['guide_step'] = step_index
    await show_guide_step(update, context)
    return GUIDE_STEP

async def cancel_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancels the guide.
    """
    await update.message.reply_text("Guide cancelled.")
    return ConversationHandler.END

guide_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("guide", start_guide)],
    states={
        GUIDE_STEP: [CallbackQueryHandler(guide_navigation_callback, pattern="^guide\..*")],
    },
    fallbacks=[CommandHandler("cancel", cancel_guide)],
)

handlers = [guide_conv_handler]
