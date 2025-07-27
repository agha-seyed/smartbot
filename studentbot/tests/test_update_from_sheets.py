import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from studentbot.utils.update_from_sheets import sync_scholarships_from_sheet, sync_faqs_from_sheet
from studentbot.utils.db import Scholarship, FAQ, get_db

class TestUpdateFromSheets(unittest.TestCase):

    @patch('studentbot.utils.update_from_sheets.get_google_sheets_client')
    def test_sync_scholarships(self, mock_get_gs_client):
        """
        Test syncing scholarships from a mock Google Sheet.
        """
        # Mock the Google Sheets client and worksheet
        mock_gs_client = MagicMock()
        mock_worksheet = MagicMock()
        mock_gs_client.open.return_value.sheet1 = mock_worksheet
        mock_get_gs_client.return_value = mock_gs_client

        # Mock the data from the sheet
        sheet_data = [
            {"ID": 1, "Title": "Scholarship 1", "Description": "Desc 1", "Link": "Link 1"},
            {"ID": 2, "Title": "Scholarship 2", "Description": "Desc 2", "Link": "Link 2"},
        ]
        mock_worksheet.get_all_records.return_value = sheet_data

        # Mock the database session
        db_session = MagicMock(spec=Session)
        db_session.query.return_value.filter_by.return_value.first.return_value = None

        # Run the sync function
        summary = sync_scholarships_from_sheet(db_session, "TestSheet")

        # Assertions
        self.assertEqual(db_session.add.call_count, 2)
        self.assertEqual(db_session.commit.call_count, 1)
        self.assertIn("2 created, 0 updated", summary)

    @patch('studentbot.utils.update_from_sheets.get_google_sheets_client')
    def test_sync_faqs(self, mock_get_gs_client):
        """
        Test syncing FAQs from a mock Google Sheet.
        """
        # Mock the Google Sheets client and worksheet
        mock_gs_client = MagicMock()
        mock_worksheet = MagicMock()
        mock_gs_client.open.return_value.sheet1 = mock_worksheet
        mock_get_gs_client.return_value = mock_gs_client

        # Mock the data from the sheet
        sheet_data = [
            {"ID": 1, "Question": "Q1", "Answer": "A1"},
            {"ID": 2, "Question": "Q2", "Answer": "A2"},
        ]
        mock_worksheet.get_all_records.return_value = sheet_data

        # Mock the database session
        db_session = MagicMock(spec=Session)
        db_session.query.return_value.filter_by.return_value.first.return_value = None

        # Run the sync function
        summary = sync_faqs_from_sheet(db_session, "TestSheet")

        # Assertions
        self.assertEqual(db_session.add.call_count, 2)
        self.assertEqual(db_session.commit.call_count, 1)
        self.assertIn("2 created, 0 updated", summary)

if __name__ == '__main__':
    unittest.main()
