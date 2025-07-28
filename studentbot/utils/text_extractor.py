# بخش: فایل‌های زیرساختی
# فایل: text_extractor.py

from PyPDF2 import PdfReader
import docx
from config import logger

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        logger.info(f"Successfully extracted text from PDF: {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    """
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        logger.info(f"Successfully extracted text from DOCX: {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        return ""
