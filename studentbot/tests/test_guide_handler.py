import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from studentbot.handlers.guide_handler import start_guide, show_guide_step, guide_navigation_callback, GUIDE_STEP

class TestGuideHandler(unittest.IsolatedAsyncioTestCase):

    @patch('studentbot.handlers.guide_handler.load_knowledge_base')
    async def test_show_guide_step(self, mock_load_knowledge_base):
        """
        Test the show_guide_step function.
        """
        # Mock the knowledge base
        mock_load_knowledge_base.return_value = {
            "guide": {
                "en": {
                    "steps": [
                        {"id": 1, "title": "Step 1", "content": "Content 1"},
                        {"id": 2, "title": "Step 2", "content": "Content 2"},
                    ]
                }
            }
        }

        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        update.message.reply_text = AsyncMock()
        context = MagicMock(spec=ContextTypes)
        context.user_data = {"lang": "en", "guide_step": 0}

        # Run the handler
        await show_guide_step(update, context)

        # Assertions
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        self.assertIn("*Step 1*", call_args[0][0])
        self.assertIn("Content 1", call_args[0][0])

    @patch('studentbot.handlers.guide_handler.show_guide_step')
    async def test_guide_navigation_callback_next(self, mock_show_guide_step):
        """
        Test the guide_navigation_callback for 'next' action.
        """
        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        query = MagicMock()
        query.data = "guide.next"
        update.callback_query = query
        context = MagicMock(spec=ContextTypes)
        context.user_data = {"guide_step": 0}

        # Run the handler
        result = await guide_navigation_callback(update, context)

        # Assertions
        self.assertEqual(result, GUIDE_STEP)
        self.assertEqual(context.user_data['guide_step'], 1)
        mock_show_guide_step.assert_called_once_with(update, context)

    @patch('studentbot.handlers.menu_handler.show_dynamic_menu')
    async def test_guide_navigation_callback_menu(self, mock_show_dynamic_menu):
        """
        Test the guide_navigation_callback for 'menu' action.
        """
        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        query = MagicMock()
        query.data = "guide.menu"
        update.callback_query = query
        context = MagicMock(spec=ContextTypes)

        # Run the handler
        result = await guide_navigation_callback(update, context)

        # Assertions
        self.assertEqual(result, ConversationHandler.END)
        mock_show_dynamic_menu.assert_called_once_with(update, context)

if __name__ == '__main__':
    unittest.main()
