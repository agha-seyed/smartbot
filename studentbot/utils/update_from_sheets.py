import gspread
from sqlalchemy.orm import Session
from studentbot.utils.db import get_db, Scholarship, FAQ
from studentbot.config import GOOGLE_CREDS, logger

def get_google_sheets_client():
    """
    Initializes and returns a gspread client.
    """
    try:
        gc = gspread.service_account(filename=GOOGLE_CREDS)
        logger.info("Successfully connected to Google Sheets API.")
        return gc
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets API: {e}")
        return None

def sync_scholarships_from_sheet(db: Session, sheet_name: str = "Scholarships"):
    """
    Syncs scholarship data from a Google Sheet to the database.
    """
    gc = get_google_sheets_client()
    if not gc:
        return "Failed to connect to Google Sheets."

    try:
        worksheet = gc.open(sheet_name).sheet1
        records = worksheet.get_all_records()

        updated_count = 0
        created_count = 0

        for record in records:
            scholarship_id = record.get("ID")
            if not scholarship_id:
                continue

            scholarship = db.query(Scholarship).filter_by(id=scholarship_id).first()
            if scholarship:
                # Update existing scholarship
                scholarship.title = record.get("Title")
                scholarship.description = record.get("Description")
                scholarship.link = record.get("Link")
                updated_count += 1
            else:
                # Create new scholarship
                new_scholarship = Scholarship(
                    id=scholarship_id,
                    title=record.get("Title"),
                    description=record.get("Description"),
                    link=record.get("Link"),
                )
                db.add(new_scholarship)
                created_count += 1

        db.commit()
        summary = f"Scholarships synced successfully. {created_count} created, {updated_count} updated."
        logger.info(summary)
        return summary

    except Exception as e:
        db.rollback()
        error_message = f"An error occurred during scholarship sync: {e}"
        logger.error(error_message)
        return error_message

def sync_faqs_from_sheet(db: Session, sheet_name: str = "FAQ"):
    """
    Syncs FAQ data from a Google Sheet to the database.
    """
    gc = get_google_sheets_client()
    if not gc:
        return "Failed to connect to Google Sheets."

    try:
        worksheet = gc.open(sheet_name).sheet1
        records = worksheet.get_all_records()

        updated_count = 0
        created_count = 0

        for record in records:
            faq_id = record.get("ID")
            if not faq_id:
                continue

            faq = db.query(FAQ).filter_by(id=faq_id).first()
            if faq:
                # Update existing FAQ
                faq.question = record.get("Question")
                faq.answer = record.get("Answer")
                updated_count += 1
            else:
                # Create new FAQ
                new_faq = FAQ(
                    id=faq_id,
                    question=record.get("Question"),
                    answer=record.get("Answer"),
                )
                db.add(new_faq)
                created_count += 1

        db.commit()
        summary = f"FAQs synced successfully. {created_count} created, {updated_count} updated."
        logger.info(summary)
        return summary

    except Exception as e:
        db.rollback()
        error_message = f"An error occurred during FAQ sync: {e}"
        logger.error(error_message)
        return error_message
