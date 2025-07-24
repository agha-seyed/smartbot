from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from utils.text_formatter import sanitize_markdown
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Stages
FAMILY_MEMBERS, ANNUAL_INCOME, PROPERTY_OWNERSHIP, PROPERTY_SIZE = range(4)

async def start_isee(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(sanitize_markdown(texts["isee_intro"]))
    await update.message.reply_text(sanitize_markdown(texts["isee_family_members"]))
    return FAMILY_MEMBERS

async def family_members(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['isee'] = {'family_members': int(update.message.text)}
    await update.message.reply_text(sanitize_markdown(texts["isee_annual_income"]))
    return ANNUAL_INCOME

async def annual_income(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['isee']['annual_income'] = float(update.message.text)
    keyboard = [
        [InlineKeyboardButton(texts["property_owner"], callback_data='owner')],
        [InlineKeyboardButton(texts["property_tenant"], callback_data='tenant')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(sanitize_markdown(texts["isee_property_ownership"]), reply_markup=reply_markup)
    return PROPERTY_OWNERSHIP

async def property_ownership(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    context.user_data['isee']['property_ownership'] = query.data
    if query.data == 'owner':
        await query.edit_message_text(text=sanitize_markdown(texts["isee_property_size"]))
        return PROPERTY_SIZE
    else:
        await calculate_and_show_isee(update, context)
        return ConversationHandler.END

async def property_size(update: Update, context: CallbackContext):
    context.user_data['isee']['property_size'] = float(update.message.text)
    await calculate_and_show_isee(update, context)
    return ConversationHandler.END


async def calculate_and_show_isee(update, context):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    isee_data = context.user_data['isee']

    family_members = isee_data['family_members']
    annual_income = isee_data['annual_income']
    property_ownership = isee_data['property_ownership']
    property_size = isee_data.get('property_size', 0)

    property_value = property_size * 500 * 0.2 if property_ownership == 'owner' else 0

    household_coefficient = 1
    if family_members == 2:
        household_coefficient = 1.57
    elif family_members == 3:
        household_coefficient = 2.04
    elif family_members == 4:
        household_coefficient = 2.46
    elif family_members >= 5:
        household_coefficient = 2.85

    isee = (annual_income + property_value) / household_coefficient

    scholarship_status = texts["scholarship_none"]
    if isee <= 27948.60:
        if isee <= (27948.60 * 0.55):
            scholarship_status = texts["scholarship_full"]
        elif isee <= (27948.60 * 0.715):
            scholarship_status = texts["scholarship_medium"]
        else:
            scholarship_status = texts["scholarship_partial"]

    result_text = texts["isee_result"].format(
        family_members=family_members,
        annual_income=annual_income,
        property_ownership=texts[f"property_{property_ownership}"],
        isee=f"{isee:.2f}",
        scholarship_status=scholarship_status
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=sanitize_markdown(result_text),
        parse_mode="MarkdownV2"
    )


async def cancel(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)
    await update.message.reply_text(texts["conversation_cancelled"])
    return ConversationHandler.END

isee_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("isee", start_isee)],
    states={
        FAMILY_MEMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, family_members)],
        ANNUAL_INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, annual_income)],
        PROPERTY_OWNERSHIP: [CallbackQueryHandler(property_ownership)],
        PROPERTY_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, property_size)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
