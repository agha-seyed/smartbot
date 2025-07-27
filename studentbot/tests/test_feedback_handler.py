import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from telegram import Update, User
from telegram.ext import ConversationHandler, ContextTypes
from studentbot.handlers.feedback_handler import ask_for_feedback, get_rating, get_comment, skip_comment, GET_RATING, GET_COMMENT

class TestFeedbackHandler(unittest.IsolatedAsyncioTestCase):

    @patch('studentbot.handlers.feedback_handler.get_db')
    async def test_get_comment(self, mock_get_db):
        """
        Test the get_comment function.
        """
        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Test", is_bot=False, full_name="Test User")
        update.message.text = "This is a test comment."

        context = MagicMock(spec=ContextTypes)
        context.user_data = {'feedback_rating': 'positive', 'current_guide_step_id': '1'}
        context.bot.send_message = AsyncMock()

        # Mock the database session
        mock_db_session = MagicMock()
        mock_get_db.return_value = iter([mock_db_session])

        # Run the handler
        result = await get_comment(update, context)

        # Assertions
        self.assertEqual(result, ConversationHandler.END)
        mock_db_session.add.assert_called_once()
        context.bot.send_message.assert_called_once()
        update.message.reply_text.assert_called_once_with("Thank you for your valuable feedback!")

    @patch('studentbot.handlers.feedback_handler.get_db')
    async def test_skip_comment(self, mock_get_db):
        """
        Test the skip_comment function.
        """
        # Mock the Update and Context objects
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Test", is_bot=False, full_name="Test User")
        query = MagicMock()
        update.callback_query = query

        context = MagicMock(spec=ContextTypes)
        context.user_data = {'feedback_rating': 'negative', 'current_guide_step_id': '2'}
        context.bot.send_message = AsyncMock()

        # Mock the database session
        mock_db_session = MagicMock()
        mock_get_db.return_value = iter([mock_db_session])

        # Run the handler
        result = await skip_comment(update, context)

        # Assertions
        self.assertEqual(result, ConversationHandler.END)
        mock_db_session.add.assert_called_once()
        context.bot.send_message.assert_called_once()
        query.message.reply_text.assert_called_once_with("Thank you for your valuable feedback!")


    async def test_ask_for_feedback(self):
        """
        Test the ask_for_feedback function.
        """
        update = MagicMock(spec=Update)
        update.message.reply_text = AsyncMock()

        result = await ask_for_feedback(update, MagicMock())

        self.assertEqual(result, GET_RATING)
        update.message.reply_text.assert_called_once()

    async def test_get_rating(self):
        """
        Test the get_rating function.
        """
        update = MagicMock(spec=Update)
        query = MagicMock()
        query.data = "feedback.positive"
        update.callback_query = query
        context = MagicMock(spec=ContextTypes)
        context.user_data = {}

        result = await get_rating(update, context)

        self.assertEqual(result, GET_COMMENT)
        self.assertEqual(context.user_data['feedback_rating'], 'positive')
        query.message.reply_text.assert_called_once_with("Thank you for your feedback! Would you like to add a comment?")

if __name__ == '__main__':
    unittest.main()
