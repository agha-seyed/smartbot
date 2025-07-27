import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from telegram import Update, User
from telegram.ext import ConversationHandler
from studentbot.handlers.consult_handler import start_consultation, get_message, GET_MESSAGE

class TestConsultHandler(unittest.IsolatedAsyncioTestCase):

    @patch('studentbot.handlers.consult_handler.get_db')
    async def test_get_message_with_text_only(self, mock_get_db):
        """
        Test the get_message function with a text-only message.
        """
        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Test", is_bot=False, full_name="Test User")
        update.message.text = "This is a test consultation request."
        update.message.caption = None
        update.message.document = None

        context = MagicMock()
        context.bot.send_message = AsyncMock()

        # Mock the database session
        mock_db_session = MagicMock()
        mock_get_db.return_value = iter([mock_db_session])

        # Run the handler
        result = await get_message(update, context)

        # Assertions
        self.assertEqual(result, ConversationHandler.END)
        mock_db_session.add.assert_called_once()
        context.bot.send_message.assert_called_once()
        update.message.reply_text.assert_called_once_with(
            "Thank you for your consultation request. We will get back to you as soon as possible."
        )

    @patch('studentbot.handlers.consult_handler.get_db')
    async def test_get_message_with_file(self, mock_get_db):
        """
        Test the get_message function with a file attachment.
        """
        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Test", is_bot=False, full_name="Test User")
        update.message.text = None
        update.message.caption = "This is a test consultation request with a file."
        update.message.document = MagicMock()
        update.message.document.file_id = "test_file_id"

        context = MagicMock()
        context.bot.send_message = AsyncMock()

        # Mock the database session
        mock_db_session = MagicMock()
        mock_get_db.return_value = iter([mock_db_session])

        # Run the handler
        result = await get_message(update, context)

        # Assertions
        self.assertEqual(result, ConversationHandler.END)
        mock_db_session.add.assert_called_once()
        context.bot.send_message.assert_called_once()
        update.message.reply_text.assert_called_once_with(
            "Thank you for your consultation request. We will get back to you as soon as possible."
        )

    async def test_start_consultation(self):
        """
        Test the start_consultation function.
        """
        update = MagicMock(spec=Update)
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        result = await start_consultation(update, context)

        self.assertEqual(result, GET_MESSAGE)
        update.message.reply_text.assert_called_once_with(
            "Please describe your consultation request. You can also attach a file (PDF, image, etc.)."
        )

if __name__ == '__main__':
    unittest.main()
