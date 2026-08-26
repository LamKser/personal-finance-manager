from typing import Dict, List

from langchain_core.tools import tool

from src.agent.tools.gg_sheet.client import client
from src.agent.tools.gg_sheet.utils import fill_date, filter_transaction


RANGE = "A:E"


# TODO: 
# - Add filter amount: float=None, transaction_type: str=None, payment_method: str=None, from_date: str=None, to_date: str=None
# - Move spreadsheet to outside
@tool
def get_transaction(sheet_name: str,
                    from_date: str=None, to_date: str=None,
                    from_amount: float=None, to_amount: float=None,
                    transaction_type: str=None, description: str=None, payment_method: str=None
                    ) -> List[List[str]]:
    """Retrieve all transaction records from a worksheet.

    Fetches the cell values for the transaction details from the specified worksheet and returns them as a list of rows.

    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").

    Returns:
        A list of rows, where each row is a list of string cell values.
        The first row typically contains the header labels.
    """
    all_transaction = client.worksheet(title=sheet_name).get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    del all_transaction
    return filtered_transaction


@tool
def get_transaction_multi_sheet(sheet_names: List[str]) -> Dict[str, List[List[str]]]:
    """Retrieve all transaction records from multiple worksheets at once.

    Fetches the cell values for the transaction details from each specified worksheet and returns them in a single mapping.

    Args:
        sheet_names (List[str]): Titles of the worksheets to read transactions from. Each entry must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").

    Returns:
        A dictionary mapping each worksheet title to its rows,
        where each row is a list of string cell values.
        The first row of each worksheet typically contains the header labels.
    """
    return {
        name: client.worksheet(title=name).get_all_values(range_name=RANGE)
        for name in sheet_names
    }


@tool
def get_all_transactions() -> Dict[str, List[List[str]]]:
    """Retrieve transaction records from every worksheet in the spreadsheet.

    Fetches the cell values for the transaction details from all worksheets and returns them in a single mapping.

    Returns:
        A dictionary mapping each worksheet title to its rows,
        where each row is a list of string cell values.
        The first row of each worksheet typically contains the header labels.
    """
    return {
        worksheet.title: worksheet.get_all_values(range_name=RANGE)
        for worksheet in client.worksheets()
    }


@tool
def count_transaction(sheet_name: str,
                      from_date: str=None, to_date: str=None,
                      from_amount: float=None, to_amount: float=None,
                      transaction_type: str=None, description: str=None, payment_method: str=None) -> int:
    """Count the number of transaction records in a worksheet.

    Reads the transaction rows from the specified worksheet and returns the total number of records, excluding the header row.

    Args:
        sheet_name (str): Title of the worksheet to count transactions from. Must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").

    Returns:
        The number of transaction records in the worksheet (excluding the header row).
    """
    all_transaction = client.worksheet(title=sheet_name).get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    del all_transaction
    return len(filtered_transaction[1:])


@tool
def count_transaction_multi_sheet(sheet_names: List[str]) -> Dict[str, int]:
    """Count transaction records in multiple worksheets at once.

    Reads the transaction rows from each specified worksheet and returns the number of records for each, excluding the header rows.

    Args:
        sheet_names (List[str]): Titles of the worksheets to count transactions from. Each entry must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").

    Returns:
        A dictionary mapping each worksheet title to its number of transaction records (excluding the header row).
    """
    return {
        name: len(client.worksheet(title=name).get_all_values(range_name=RANGE)[1:])
        for name in sheet_names
    }


@tool
def count_all_transactions() -> Dict[str, int]:
    """Count transaction records in every worksheet of the spreadsheet.

    Reads the transaction rows from all worksheets and returns the number of records for each, excluding the header rows.

    Returns:
        A dictionary mapping each worksheet title to its number of transaction records (excluding the header row).
    """
    return {
        worksheet.title: len(worksheet.get_all_values(range_name=RANGE)[1:])
        for worksheet in client.worksheets()
    }
