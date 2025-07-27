import unittest
from unittest.mock import MagicMock, AsyncMock
from telegram import Update
from telegram.ext import ContextTypes
from studentbot.utils.lang import language_decorator

class TestLangDecorator(unittest.IsolatedAsyncioTestCase):

    async def test_language_decorator_sets_default_lang(self):
        """
        Test that the language_decorator sets the default language to 'en'
        if it's not already set in the context.
        """
        # A mock async function to be decorated
        @language_decorator
        async def decorated_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            return context.user_data.get('lang')

        # Mock Update and Context objects
        update = MagicMock(spec=Update)
        context = MagicMock(spec=ContextTypes)
        context.user_data = {}

        # Call the decorated function
        result = await decorated_function(update, context)

        # Assertions
        self.assertEqual(result, 'en')
        self.assertEqual(context.user_data['lang'], 'en')

    async def test_language_decorator_preserves_existing_lang(self):
        """
        Test that the language_decorator does not overwrite an existing
        language setting in the context.
        """
        # A mock async function to be decorated
        @language_decorator
        async def decorated_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
            return context.user_data.get('lang')

        # Mock Update and Context objects
        update = MagicMock(spec=Update)
        context = MagicMock(spec=ContextTypes)
        context.user_data = {'lang': 'fa'}

        # Call the decorated function
        result = await decorated_function(update, context)

        # Assertions
        self.assertEqual(result, 'fa')
        self.assertEqual(context.user_data['lang'], 'fa')

if __name__ == '__main__':
    unittest.main()
