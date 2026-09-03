from typing import Dict, List

from langchain_core.tools import tool

from src.agent.tools.gg_sheet.client import client
from src.agent.tools.gg_sheet.utils import fill_date, filter_transaction


RANGE = "A:E"


@tool
def get_transaction(sheet_name: str,
                    from_date: str = None, to_date: str = None,
                    from_amount: float = None, to_amount: float = None,
                    transaction_type: str = None, description: str = None, payment_method: str = None
                    ) -> List[List[str]]:
    """Retrieve transaction records from a worksheet with optional filtering.

    Fetches the cell values for the transaction details from the specified worksheet, applies filters based on the provided criteria and returns them as a list of rows.

    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        from_date (str, optional): Start date for filtering in 'DD-MM-YYYY' format.
        to_date (str, optional): End date for filtering in 'DD-MM-YYYY' format.
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (str, optional): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (str, optional): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        List[List[str]]: A list of rows, where each row is a list of string cell values. The first row typically contains the header labels.
    """
    all_transaction = client.worksheet(title=sheet_name).get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    return filtered_transaction


@tool
def get_transaction_multi_sheet(sheet_names: List[str],
                                from_amount: float = None, to_amount: float = None,
                                transaction_type: str = None, description: str = None, payment_method: str = None
                                ) -> Dict[str, List[List[str]]]:
    """Retrieve all transaction records from multiple worksheets at once.

    Fetches the cell values for the transaction details from each specified worksheet and returns them in a single mapping.

    Args:
        sheet_names (List[str]): Titles of the worksheets to read transactions from. Each entry must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (str, optional): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (str, optional): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).
    Returns:
        Dict[str, List[List[str]]]: A dictionary mapping each worksheet title to its rows, where each row is a list of string cell values. The first row of each worksheet typically contains the header labels.
    """
    result = dict()
    for name in sheet_names:
        all_transaction = client.worksheet(title=name).get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[name] = filtered_transaction
    return result


@tool
def get_all_transactions(from_amount: float = None, to_amount: float = None,
                        transaction_type: str = None, description: str = None, payment_method: str = None
                        ) -> Dict[str, List[List[str]]]:
    """Retrieve transaction records from every worksheet in the spreadsheet.

    Fetches the cell values for the transaction details from all worksheets and returns them in a single mapping.

    Args:
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (str, optional): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (str, optional): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        Dict[str, List[List[str]]]: A dictionary mapping each worksheet title to its rows, where each row is a list of string cell values.
    """
    all_worksheets = client.worksheets()
    result = dict()
    for worksheet in all_worksheets:
        if worksheet.title == "Tổng hợp":
            continue
        all_transaction = worksheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[worksheet.title] = filtered_transaction
    return result


@tool
def count_transaction(sheet_name: str,
                      from_date: str = None, to_date: str = None,
                      from_amount: float = None, to_amount: float = None,
                      transaction_type: str = None, description: str = None, payment_method: str = None) -> int:
    """Count the number of transaction records in a worksheet with optional filtering.

    Reads the transaction rows from the specified worksheet, applies filters based on the provided criteria, and returns the total number of matching records.

    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        from_date (str, optional): Start date for filtering in 'DD-MM-YYYY' format.
        to_date (str, optional): End date for filtering in 'DD-MM-YYYY' format.
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (str, optional): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (str, optional): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        int: The number of transaction records matching the criteria.
    """
    all_transaction = client.worksheet(title=sheet_name).get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    return len(filtered_transaction) - 1 # Skip header row


@tool
def count_transaction_multi_sheet(sheet_names: List[str],
                                  from_amount: float = None, to_amount: float = None,
                                transaction_type: str = None, description: str = None, payment_method: str = None
                                ) -> Dict[str, int]:
    """Count transaction records in multiple worksheets at once.

    Reads the transaction rows from each specified worksheet and returns the number of records for each, excluding the header rows.

    Args:
        sheet_names (List[str]): Titles of the worksheets to read transactions from. Each entry must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (str, optional): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (str, optional): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).
    
    Returns:
        Dict[str, int]: A dictionary mapping each worksheet title to its number of transaction records (excluding the header row).
    """
    result = dict()
    for name in sheet_names:
        all_transaction = client.worksheet(title=name).get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[name] = len(filtered_transaction) - 1 # Skip header row
    return result


@tool
def count_all_transactions(from_amount: float = None, to_amount: float = None,
                        transaction_type: str = None, description: str = None, payment_method: str = None
                        ) -> Dict[str, int]:
    """Count transaction records in every worksheet of the spreadsheet.

    Reads the transaction rows from all worksheets and returns the number of records for each, excluding the header rows.
    
    Args:
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (str, optional): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (str, optional): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        Dict[str, int]: A dictionary mapping each worksheet title to its number of transaction records (excluding the header row).
    """
    all_worksheets = client.worksheets()
    result = dict()
    for worksheet in all_worksheets:
        if worksheet.title == "Tổng hợp":
            continue
        all_transaction = worksheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[worksheet.title] = len(filtered_transaction) - 1 # Skip header row
    return result
