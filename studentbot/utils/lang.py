from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

def language_decorator(func):
    """
    A decorator that sets the user's language in the context.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if 'lang' not in context.user_data:
            context.user_data['lang'] = 'en'  # Default to English
        return await func(update, context, *args, **kwargs)
    return wrapper
