import unittest

class TestEnvironment(unittest.TestCase):
    def test_imports(self):
        """
        Test that all required modules can be imported.
        """
        try:
            import telegram
            import sqlalchemy
            import redis
            import gspread
            import oauth2client
            import requests
            import dotenv
            import psycopg2
            import fuzzywuzzy
            import Levenshtein
            import bcrypt
            import pytest
            import mock
        except ImportError as e:
            self.fail(f"Failed to import a required module: {e}")
