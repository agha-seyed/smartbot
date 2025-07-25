from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from config import logger

async def scholarships_menu(update: Update, context: CallbackContext):
    """Shows the scholarships menu."""
    logger.info(f"User {update.effective_user.id} requested the scholarships menu.")
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Conditions", callback_data='scholarships_conditions')],
        [InlineKeyboardButton("Documents", callback_data='scholarships_documents')],
        [InlineKeyboardButton("Deadlines", callback_data='scholarships_deadlines')],
        [InlineKeyboardButton("Uni-Italia.it Links", callback_data='scholarships_uni_italia_links')],
        [InlineKeyboardButton("Back", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Scholarships Menu:", reply_markup=reply_markup)

async def migration_steps_menu(update: Update, context: CallbackContext):
    """Shows the migration steps menu."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Visa", callback_data='migration_visa')],
        [InlineKeyboardButton("Embassy Appointment", callback_data='migration_embassy_appointment')],
        [InlineKeyboardButton("Documents", callback_data='migration_documents')],
        [InlineKeyboardButton("Back", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Migration Steps Menu:", reply_markup=reply_markup)

async def housing_menu(update: Update, context: CallbackContext):
    """Shows the housing menu."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Dormitory", callback_data='housing_dormitory')],
        [InlineKeyboardButton("Rental", callback_data='housing_rental')],
        [InlineKeyboardButton("Safe Areas", callback_data='housing_safe_areas')],
        [InlineKeyboardButton("Back", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Housing Menu:", reply_markup=reply_markup)

async def student_life_menu(update: Update, context: CallbackContext):
    """Shows the student life menu."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Transportation", callback_data='student_life_transportation')],
        [InlineKeyboardButton("SIM Card", callback_data='student_life_sim_card')],
        [InlineKeyboardButton("Bank", callback_data='student_life_bank')],
        [InlineKeyboardButton("Shopping", callback_data='student_life_shopping')],
        [InlineKeyboardButton("Back", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Student Life Menu:", reply_markup=reply_markup)

async def universities_menu(update: Update, context: CallbackContext):
    """Shows the universities menu."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Majors", callback_data='universities_majors')],
        [InlineKeyboardButton("Offices", callback_data='universities_offices')],
        [InlineKeyboardButton("Links", callback_data='universities_links')],
        [InlineKeyboardButton("Back", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Universities Menu:", reply_markup=reply_markup)

async def tools_menu(update: Update, context: CallbackContext):
    """Shows the tools menu."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Cost of Living", callback_data='tools_cost_of_living')],
        [InlineKeyboardButton("Student Discounts", callback_data='tools_student_discounts')],
        [InlineKeyboardButton("ISEE Calculator", callback_data='isee')],
        [InlineKeyboardButton("Perugia Weather", callback_data='weather')],
        [InlineKeyboardButton("Back", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Tools Menu:", reply_markup=reply_markup)

async def language_courses_menu(update: Update, context: CallbackContext):
    """Shows the language courses menu."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("CELI", callback_data='language_celi')],
        [InlineKeyboardButton("CILS", callback_data='language_cils')],
        [InlineKeyboardButton("PLIDA", callback_data='language_plida')],
        [InlineKeyboardButton("Back", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Language Courses Menu:", reply_markup=reply_markup)

import feedparser

async def university_news_menu(update: Update, context: CallbackContext):
    """Shows the university news menu."""
    query = update.callback_query
    await query.answer()

    feeds = {
        "Uni-Italia.it": "https://www.uni-italia.it/rss.xml",
        "ANSA.it": "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
    }

    news_items = []
    for feed_name, feed_url in feeds.items():
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            news_items.append(f"<a href='{entry.link}'>{entry.title}</a>")

    if news_items:
        await query.message.reply_text("\n\n".join(news_items), parse_mode="HTML", disable_web_page_preview=True)
    else:
        await query.message.reply_text("Could not retrieve news at this time.")

from telegram.ext import ConversationHandler

USER_FEEDBACK = range(1)

async def user_feedback_menu(update: Update, context: CallbackContext):
    """Shows the user feedback menu."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await query.message.reply_text(texts.get("user_feedback_prompt", "Please send us your feedback:"))
    return USER_FEEDBACK

submenu_handlers = [
    CallbackQueryHandler(scholarships_menu, pattern='^scholarships$'),
    CallbackQueryHandler(migration_steps_menu, pattern='^migration_steps$'),
    CallbackQueryHandler(housing_menu, pattern='^housing$'),
    CallbackQueryHandler(student_life_menu, pattern='^student_life$'),
    CallbackQueryHandler(universities_menu, pattern='^universities$'),
    CallbackQueryHandler(tools_menu, pattern='^tools$'),
    CallbackQueryHandler(language_courses_menu, pattern='^language_courses$'),
from .cmd_start import show_main_menu

async def back_to_main_menu(update: Update, context: CallbackContext):
    """Shows the main menu."""
    query = update.callback_query
    await query.answer()
    # This is a bit of a hack, but it works for now.
    # We need to create a new update object with a message attribute.
    class MockMessage:
        def __init__(self, chat_id, message_id):
            self.chat_id = chat_id
            self.message_id = message_id
        async def reply_text(self, text, reply_markup, parse_mode):
            await context.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )

    class MockUpdate:
        def __init__(self, chat_id, message_id):
            self.message = MockMessage(chat_id, message_id)

    await show_main_menu(MockUpdate(query.message.chat_id, query.message.message_id), context)


submenu_handlers = [
    CallbackQueryHandler(scholarships_menu, pattern='^scholarships$'),
    CallbackQueryHandler(migration_steps_menu, pattern='^migration_steps$'),
    CallbackQueryHandler(housing_menu, pattern='^housing$'),
    CallbackQueryHandler(student_life_menu, pattern='^student_life$'),
    CallbackQueryHandler(universities_menu, pattern='^universities$'),
    CallbackQueryHandler(tools_menu, pattern='^tools$'),
    CallbackQueryHandler(language_courses_menu, pattern='^language_courses$'),
async def tools_cost_of_living(update: Update, context: CallbackContext):
    """Shows the cost of living information."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await query.message.reply_text(texts.get("cost_of_living_text", "This feature is under construction."))

async def tools_student_discounts(update: Update, context: CallbackContext):
    """Shows the student discounts information."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await query.message.reply_text(texts.get("student_discounts_text", "This feature is under construction."))

submenu_handlers = [
    CallbackQueryHandler(scholarships_menu, pattern='^scholarships$'),
    CallbackQueryHandler(migration_steps_menu, pattern='^migration_steps$'),
    CallbackQueryHandler(housing_menu, pattern='^housing$'),
    CallbackQueryHandler(student_life_menu, pattern='^student_life$'),
    CallbackQueryHandler(universities_menu, pattern='^universities$'),
    CallbackQueryHandler(tools_menu, pattern='^tools$'),
    CallbackQueryHandler(language_courses_menu, pattern='^language_courses$'),
    CallbackQueryHandler(university_news_menu, pattern='^university_news$'),
    CallbackQueryHandler(user_feedback_menu, pattern='^user_feedback$'),
    CallbackQueryHandler(back_to_main_menu, pattern='^main_menu$'),
async def language_celi(update: Update, context: CallbackContext):
    """Shows the CELI information."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await query.message.reply_text(texts.get("celi_text", "This feature is under construction."))

async def language_cils(update: Update, context: CallbackContext):
    """Shows the CILS information."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await query.message.reply_text(texts.get("cils_text", "This feature is under construction."))

async def language_plida(update: Update, context: CallbackContext):
    """Shows the PLIDA information."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await query.message.reply_text(texts.get("plida_text", "This feature is under construction."))

submenu_handlers = [
    CallbackQueryHandler(scholarships_menu, pattern='^scholarships$'),
    CallbackQueryHandler(migration_steps_menu, pattern='^migration_steps$'),
    CallbackQueryHandler(housing_menu, pattern='^housing$'),
    CallbackQueryHandler(student_life_menu, pattern='^student_life$'),
    CallbackQueryHandler(universities_menu, pattern='^universities$'),
    CallbackQueryHandler(tools_menu, pattern='^tools$'),
    CallbackQueryHandler(language_courses_menu, pattern='^language_courses$'),
    CallbackQueryHandler(university_news_menu, pattern='^university_news$'),
    CallbackQueryHandler(user_feedback_menu, pattern='^user_feedback$'),
    CallbackQueryHandler(back_to_main_menu, pattern='^main_menu$'),
    CallbackQueryHandler(tools_cost_of_living, pattern='^tools_cost_of_living$'),
    CallbackQueryHandler(tools_student_discounts, pattern='^tools_student_discounts$'),
    CallbackQueryHandler(language_celi, pattern='^language_celi$'),
    CallbackQueryHandler(language_cils, pattern='^language_cils$'),
    CallbackQueryHandler(language_plida, pattern='^language_plida$'),
]
