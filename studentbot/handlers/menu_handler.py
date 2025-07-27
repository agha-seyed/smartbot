import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from studentbot.config import logger
from studentbot.utils.menu_utils import load_texts

def load_menu_structure():
    """
    Loads the menu structure from the menus.json file.
    """
    try:
        with open('studentbot/config/menus.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading menu structure: {e}")
        return {}

async def show_dynamic_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, menu_path: str = "main_menu"):
    """
    Displays a dynamic menu based on the user's path.
    """
    user_lang = context.user_data.get("lang", "fa")
    menu_structure = load_menu_structure()

    # Navigate to the correct menu
    path_parts = menu_path.split('.')
    current_menu = menu_structure
    for part in path_parts:
        current_menu = current_menu.get(part, {})

    if not current_menu:
        await update.callback_query.message.reply_text("Menu not found.")
        return

    buttons = current_menu.get("buttons", {})
    keyboard = []

    if "dynamic_data" in current_menu:
        dynamic_func_name = current_menu["dynamic_data"]
        if dynamic_func_name in globals():
            dynamic_buttons = await globals()[dynamic_func_name](context)
            keyboard.extend(dynamic_buttons)

    for key, value in buttons.items():
        button_text = value.get(user_lang, key)
        callback_data = f"menu.{menu_path}.{key}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

    # Add back button if not in main menu
    if menu_path != "main_menu":
        parent_path = ".".join(path_parts[:-2])
        if not parent_path:
            parent_path = "main_menu"
        back_button_text = load_texts(user_lang).get("back", "Back")
        keyboard.append([InlineKeyboardButton(back_button_text, callback_data=f"menu.{parent_path}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = update.message or update.callback_query.message
    await message.reply_text("Please select an option:", reply_markup=reply_markup)

async def dynamic_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles all dynamic menu callbacks.
    """
    query = update.callback_query
    await query.answer()

    parts = query.data.split('.')
    menu_path = ".".join(parts[1:])

    # Find the menu in the structure
    menu_structure = load_menu_structure()
    current_menu = menu_structure
    for part in parts[1:]:
        if 'submenus' in current_menu and part in current_menu['submenus']:
            current_menu = current_menu['submenus'][part]
        elif 'buttons' in current_menu and part in current_menu['buttons']:
            # This is a leaf node, trigger an action
            action = part
            logger.info(f"User {update.effective_user.id} selected action '{action}' from menu '{'.'.join(parts[1:-1])}'")
            await query.message.reply_text(f"You selected: {action}")
            return
        else:
            current_menu = None
            break

    if current_menu:
        await show_dynamic_menu(update, context, menu_path=menu_path)
    else:
        # Fallback to the old logic if the menu is not in the new structure
        from .submenu_handler import submenu_callback
        await submenu_callback(update, context)

async def fetch_scholarships(context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches scholarship data and returns a list of buttons.
    """
    # In a real application, you would fetch this from the database
    # For now, we'll just return some dummy data
    dummy_scholarships = [
        {"id": 1, "title": "Scholarship A"},
        {"id": 2, "title": "Scholarship B"},
    ]

    buttons = []
    for scholarship in dummy_scholarships:
        button_text = scholarship["title"]
        callback_data = f"scholarship.{scholarship['id']}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

    return buttons

handlers = [
    CommandHandler("menu", show_dynamic_menu),
    CallbackQueryHandler(dynamic_menu_callback, pattern="^menu\."),
]
