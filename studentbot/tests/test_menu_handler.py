import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from telegram import Update, User
from telegram.ext import ContextTypes
from studentbot.handlers.menu_handler import show_dynamic_menu, dynamic_menu_callback

class TestMenuHandler(unittest.IsolatedAsyncioTestCase):

    @patch('studentbot.handlers.menu_handler.load_menu_structure')
    async def test_show_dynamic_menu(self, mock_load_menu_structure):
        """
        Test the show_dynamic_menu function.
        """
        # Mock the menu structure
        mock_load_menu_structure.return_value = {
            "main_menu": {
                "buttons": {
                    "profile": {"en": "My Profile", "fa": "پروفایل من"},
                    "scholarships": {"en": "Scholarships", "fa": "بورسیه‌ها"},
                }
            }
        }

        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        update.message.reply_text = AsyncMock()
        context = MagicMock(spec=ContextTypes)
        context.user_data = {"lang": "en"}

        # Run the handler
        await show_dynamic_menu(update, context)

        # Assertions
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        self.assertIn("Please select an option:", call_args[0])
        reply_markup = call_args[1]['reply_markup']
        self.assertEqual(len(reply_markup.inline_keyboard), 2)
        self.assertEqual(reply_markup.inline_keyboard[0][0].text, "My Profile")

    @patch('studentbot.handlers.menu_handler.load_menu_structure')
    @patch('studentbot.handlers.menu_handler.show_dynamic_menu')
    async def test_dynamic_menu_callback_navigation(self, mock_show_dynamic_menu, mock_load_menu_structure):
        """
        Test that the dynamic_menu_callback correctly handles menu navigation.
        """
        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        query = MagicMock()
        # Mock the menu structure
        mock_load_menu_structure.return_value = {
            "main_menu": {
                "submenus": {
                    "scholarships": {}
                }
            }
        }

        query.data = "menu.main_menu.scholarships"
        update.callback_query = query
        context = MagicMock(spec=ContextTypes)

        # Run the handler
        await dynamic_menu_callback(update, context)

        # Assertions
        mock_show_dynamic_menu.assert_called_once_with(update, context, menu_path="main_menu.scholarships")

if __name__ == '__main__':
    unittest.main()
