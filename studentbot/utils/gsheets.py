# بخش: فایل‌های زیرساختی
# فایل: gsheets.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_CREDS, QUESTIONS_SHEET_NAME, logger
import os

def get_gspread_client():
    """
    Initialize and return a gspread client using Google service account credentials.

    Returns:
        gspread.Client: Authorized gspread client.
    """
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        if not os.path.exists(GOOGLE_CREDS):
            logger.error(f"Google credentials file not found at: {GOOGLE_CREDS}")
            raise FileNotFoundError(f"Google credentials file not found at: {GOOGLE_CREDS}")
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, scope)
        client = gspread.authorize(credentials)
        logger.info("Successfully authorized gspread client.")
        return client
    except Exception as e:
        logger.error(f"Error initializing gspread client: {e}")
        raise

def append_to_sheet(sheet_name: str, data: list):
    """
    Append a row of data to the specified Google Sheet.

    Args:
        sheet_name (str): Name of the Google Sheet.
        data (list): List of values to append as a row.
    """
    try:
        client = get_gspread_client()
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.get_worksheet(0)  # Use the first worksheet
        worksheet.append_row(data)
        logger.info(f"Successfully appended data to sheet '{sheet_name}': {data}")
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"Google Sheet '{sheet_name}' not found.")
        raise
    except gspread.exceptions.APIError as e:
        logger.error(f"Google Sheets API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error appending data to sheet '{sheet_name}': {e}")
        raise

def save_question(user_id: int, question: str, timestamp: str):
    """
    Save a user's question to the Google Sheet specified by QUESTIONS_SHEET_NAME.

    Args:
        user_id (int): Telegram user ID.
        question (str): The question text.
        timestamp (str): Timestamp of the question submission.
    """
    try:
        data = [user_id, question, timestamp]
        append_to_sheet(QUESTIONS_SHEET_NAME, data)
        logger.info(f"Question saved for user {user_id} in sheet '{QUESTIONS_SHEET_NAME}'")
    except Exception as e:
        logger.error(f"Error saving question for user {user_id}: {e}")
        raise
