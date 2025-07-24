import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_CREDS, SPREADSHEET_NAME

def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)
    return spreadsheet.worksheet(sheet_name)

def save_to_gsheets(data, sheet_name):
    sheet = get_sheet(sheet_name)
    sheet.append_row(list(data.values()))

def update_knowledge_base_from_gsheets():
    # This function will be called periodically to update the knowledge base
    # For now, it's a placeholder
    pass
