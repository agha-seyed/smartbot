import unittest
from unittest.mock import patch, MagicMock
from telegram import Update, User as TelegramUser, Message, Chat
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters
from studentbot.main import main
import asyncio

class FullTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.app = Application.builder().token("test_token").build()

    def tearDown(self):
        self.loop.close()

    def test_full_flow(self):
        async def run_test():
            # Mock update and context
            user = TelegramUser(id=123, first_name="Test", is_bot=False)
            chat = Chat(id=123, type="private")
            message = Message(message_id=1, date=None, chat=chat, from_user=user)
            update = Update(update_id=1, message=message)
            context = ContextTypes.DEFAULT_TYPE(application=self.app)

            # 1. Start and select language
            with patch('telegram.ext.Application.bot') as mock_bot:
                await self.app.process_update(update)
                # Here you would check the bot's response

            # 2. Create profile
            update.message.text = "/profile"
            await self.app.process_update(update)
            # ... and so on for all the other tests

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
