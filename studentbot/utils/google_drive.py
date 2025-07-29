# بخش: فایل‌های زیرساختی
# فایل: google_drive.py

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from studentbot.config import logger, GOOGLE_DRIVE_UPLOAD_FOLDER_ID

def get_drive_client():
    """
    Initialize and return a PyDrive client.
    """
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Creates local webserver and handles authentication.
        drive = GoogleDrive(gauth)
        logger.info("Successfully authorized PyDrive client.")
        return drive
    except Exception as e:
        logger.error(f"Error initializing PyDrive client: {e}")
        raise

def upload_file_to_drive(file_path: str, file_name: str) -> str:
    """
    Upload a file to the specified Google Drive folder.
    """
    try:
        drive = get_drive_client()
        file_drive = drive.CreateFile({
            'title': file_name,
            'parents': [{'id': GOOGLE_DRIVE_UPLOAD_FOLDER_ID}]
        })
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
        logger.info(f"Successfully uploaded file '{file_name}' to Google Drive.")
        return file_drive['alternateLink']
    except Exception as e:
        logger.error(f"Error uploading file '{file_name}' to Google Drive: {e}")
        raise
