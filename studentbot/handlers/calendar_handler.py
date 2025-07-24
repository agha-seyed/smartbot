from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from telegram_inline_calendar import TGCalendar
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def show_calendar(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    calendar, step = TGCalendar().build()
    await update.message.reply_text(
        text=texts["calendar_select_date"],
        reply_markup=calendar
    )

async def calendar_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    result, key, step = TGCalendar().process(query.data)

    if not result and key:
        await context.bot.edit_message_text(
            text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=key
        )
    elif result:
        await context.bot.edit_message_text(
            text=f"You selected {result}",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

calendar_start_handler = CommandHandler("calendar", show_calendar)
calendar_callback_handler = CallbackQueryHandler(calendar_callback)
