import gspread

from src.settings import settings


def google_sheet_client():
    client = gspread.service_account(filename=settings.credential)
    spreadsheet = client.open_by_key(key=settings.sheet_key)
    return spreadsheet

client = google_sheet_client()