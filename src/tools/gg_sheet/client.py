

from logging import getLogger

import gspread

from src.settings import settings

log = getLogger(__name__)

class GSheetClient:

    _instance = None

    @classmethod
    def get_spreadsheet(cls):
        if cls._instance is None:
            try:
                log.info("[GSHEET] - Connecting to Google Sheets...")
                gc = gspread.service_account(filename=settings.credential)
                cls._instance = gc.open_by_key(key=settings.sheet_key)
                log.info("[GSHEET] - Successfully connected to Spreadsheet: %s", cls._instance.title)
            except Exception as e:
                log.error("[GSHEET] - Failed to connect to Google Sheets: %s", e)
                raise ConnectionError(f"Could not connect to Google Sheets. Please check credentials, sheet key or network connection. Error: {e}")
        return cls._instance


def get_client():
    return GSheetClient.get_spreadsheet()

