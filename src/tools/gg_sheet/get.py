

from typing import Dict, List, Literal
from logging import getLogger

log = getLogger(__name__)

import numpy as np
from langchain_core.tools import tool

from src.schema import ToolResult
from src.tools.gg_sheet.client import get_client
from src.tools.gg_sheet.utils import fill_date, filter_transaction, convert_amount_to_float


RANGE = "A:E"

# ================================ GET Action ================================
@tool
def get_transaction(sheet_name: str,
                    from_date: str = None, to_date: str = None,
                    from_amount: float = None, to_amount: float = None,
                    transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                    payment_method: Literal["Thẻ", "Tiền mặt"] | None = None
                    ) -> ToolResult:
    """Retrieve transaction records from a worksheet with optional filtering.

    Fetches the cell values for the transaction details from the specified worksheet, applies filters based on the provided criteria and returns them as a list of rows.

    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        from_date (str, optional): Start date for filtering in 'DD-MM-YYYY' format.
        to_date (str, optional): End date for filtering in 'DD-MM-YYYY' format.
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        List[List[str]]: A list of rows, where each row is a list of string cell values. The first row typically contains the header labels.
    """
    log.info("[TOOL-`get_transaction`] Execute tool")
    sheet = get_client().worksheet(title=sheet_name)
    all_transaction = sheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    log.info("[TOOL-`get_transaction`] Tool executed successfully")
    return ToolResult(
        result=filtered_transaction,
        reference={
            sheet_name: sheet.url
        }
    )


@tool
def get_transaction_multi_sheet(sheet_names: List[str],
                                from_amount: float = None, to_amount: float = None,
                                transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                                payment_method: Literal["Thẻ", "Tiền mặt"] | None = None
                                ) -> ToolResult:
    """Retrieve all transaction records from multiple worksheets at once.

    Fetches the cell values for the transaction details from each specified worksheet and returns them in a single mapping.

    Args:
        sheet_names (List[str]): Titles of the worksheets to read transactions from. Each entry must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        Dict[str, List[List[str]]]: A dictionary mapping each worksheet title to its rows, where each row is a list of string cell values. The first row of each worksheet typically contains the header labels.
    """
    log.info("[TOOL-`get_transaction_multi_sheet`] Execute tool")
    result = dict()
    sheet_url = dict()
    client = get_client()
    for name in sheet_names:
        sheet = client.worksheet(title=name)
        all_transaction = sheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[name] = filtered_transaction
        sheet_url[name] = sheet.url
    log.info("[TOOL-`get_transaction_multi_sheet`] Tool executed successfully")
    return ToolResult(
        result=result,
        reference=sheet_url
    )


@tool
def get_all_transactions(from_amount: float = None, to_amount: float = None,
                        transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                        payment_method: Literal["Thẻ", "Tiền mặt"] | None = None
                        ) -> ToolResult:
    """Retrieve transaction records from every worksheet in the spreadsheet.

    Fetches the cell values for the transaction details from all worksheets and returns them in a single mapping.

    Args:
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        Dict[str, List[List[str]]]: A dictionary mapping each worksheet title to its rows, where each row is a list of string cell values.
    """
    log.info("[TOOL-`get_all_transactions`] Execute tool")
    all_worksheets = get_client().worksheets()
    result = dict()
    sheet_url = dict()
    for worksheet in all_worksheets:
        if worksheet.title == "Tổng hợp":
            continue
        all_transaction = worksheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[worksheet.title] = filtered_transaction
        sheet_url[worksheet.title] = worksheet.url
    log.info("[TOOL-`get_all_transactions`] Tool executed successfully")
    return ToolResult(
        result=result,
        reference=sheet_url
    )


# ================================ COUNT Action ================================
@tool
def count_transaction(sheet_name: str,
                      from_date: str = None, to_date: str = None,
                      from_amount: float = None, to_amount: float = None,
                      transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                      payment_method: Literal["Thẻ", "Tiền mặt"] | None = None) -> ToolResult:
    """Count the number of transaction records in a worksheet with optional filtering.

    Reads the transaction rows from the specified worksheet, applies filters based on the provided criteria, and returns the total number of matching records.

    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        from_date (str, optional): Start date for filtering in 'DD-MM-YYYY' format.
        to_date (str, optional): End date for filtering in 'DD-MM-YYYY' format.
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        int: The number of transaction records matching the criteria.
    """
    log.info("[TOOL-`count_transaction`] Execute tool")
    sheet = get_client().worksheet(title=sheet_name)
    all_transaction = sheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    log.info("[TOOL-`count_transaction`] Tool executed successfully")
    return ToolResult(
        result=len(filtered_transaction) - 1, # Skip header row
        reference={sheet_name: sheet.url}
    )


@tool
def count_transaction_multi_sheet(sheet_names: List[str],
                                from_amount: float = None, to_amount: float = None,
                                transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                                payment_method: Literal["Thẻ", "Tiền mặt"] | None = None
                                ) -> ToolResult:
    """Count transaction records in multiple worksheets at once.

    Reads the transaction rows from each specified worksheet and returns the number of records for each, excluding the header rows.

    Args:
        sheet_names (List[str]): Titles of the worksheets to read transactions from. Each entry must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).
    
    Returns:
        Dict[str, int]: A dictionary mapping each worksheet title to its number of transaction records (excluding the header row).
    """
    log.info("[TOOL-`count_transaction_multi_sheet`] Execute tool")
    result = dict()
    sheet_url = dict()
    client = get_client()
    for name in sheet_names:
        sheet = client.worksheet(title=name)
        all_transaction = sheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[name] = len(filtered_transaction) - 1 # Skip header row
        sheet_url[name] = sheet.url
    log.info("[TOOL-`count_transaction_multi_sheet`] Tool executed successfully")
    return ToolResult(
        result=result,
        reference=sheet_url
    )


@tool
def count_all_transactions(from_amount: float = None, to_amount: float = None,
                        transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                        payment_method: Literal["Thẻ", "Tiền mặt"] | None = None
                        ) -> ToolResult:
    """Count transaction records in every worksheet of the spreadsheet.

    Reads the transaction rows from all worksheets and returns the number of records for each, excluding the header rows.
    
    Args:
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns:
        Dict[str, int]: A dictionary mapping each worksheet title to its number of transaction records (excluding the header row).
    """
    log.info("[TOOL-`count_all_transactions`] Execute tool")
    all_worksheets = get_client().worksheets()
    result = dict()
    sheet_url = dict()
    for worksheet in all_worksheets:
        if worksheet.title == "Tổng hợp":
            continue
        all_transaction = worksheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, None, None, from_amount, to_amount, transaction_type, description, payment_method)
        result[worksheet.title] = len(filtered_transaction) - 1 # Skip header row
        sheet_url[worksheet.title] = worksheet.url
    log.info("[TOOL-`count_all_transactions`] Tool executed successfully")
    return ToolResult(
        result=result,
        reference=sheet_url
    )


@tool
def count_distribution_transaction(sheet_name: str, by: Literal["date", "transaction_type", "payment_method"]) -> ToolResult:
    """Count transactions in a worksheet grouped by a specified field.

    Args:
        sheet_name: Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        by: The field used to group transactions. Supported values are:
            - 'date': Group transactions by date.
            - 'transaction_type': Group transactions by transaction type.
            - 'payment_method': Group transactions by payment method.
    Returns: 
        Dict[str, int]: A dictionary mapping each distinct value of the selected field to the number of transactions with that value.
    """
    log.info("[TOOL-`count_distribution_transaction`] Execute tool")
    distribution = dict()
    sheet = get_client().worksheet(title=sheet_name)
    all_transaction = sheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    for transaction in all_transaction:
        by_dict = {
            "date": transaction[0],
            "transaction_type": transaction[2],
            "payment_method": transaction[4]
        }
        type_count = by_dict[by]
        distribution[type_count] = distribution.get(type_count, 0) + 1

    log.info("[TOOL-`count_distribution_transaction`] Tool executed successfully")
    return ToolResult(
        result=distribution,
        reference=sheet.url
    )


@tool
def count_distribution_transaction_multi_sheet(sheet_names: List[str], by: Literal["date", "transaction_type", "payment_method"]) -> ToolResult:
    """Count transactions of one or more worksheet grouped by a specified field.

    Args:
        sheet_names (List[str]): Titles of the worksheets to read transactions from. Each entry must be either "Tổng hợp" (the summary sheet) or "Tháng X", where X is the month number (e.g., "Tháng 1" through "Tháng 12").
        by (Literal["date", "transaction_type", "payment_method"]): The field used to group transactions. Supported values are:
            - 'date': Group transactions by date.
            - 'transaction_type': Group transactions by transaction type.
            - 'payment_method': Group transactions by payment method.
    Returns: 
        Dict[str, int]: A dictionary mapping each distinct value of the selected field to the number of transactions with that value.
    """
    log.info("[TOOL-`count_distribution_transaction`] Execute tool")
    distribution = dict()
    sheet_url = dict()
    client = get_client()
    for name in sheet_names:
        distribution[name] = dict()
        sheet = client.worksheet(title=name)
        all_transaction = sheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        
        for transaction in all_transaction:
            by_dict = {
                "date": transaction[0],
                "transaction_type": transaction[2],
                "payment_method": transaction[4]
            }
            type_count = by_dict[by]
            distribution[name][type_count] = distribution[name].get(type_count, 0) + 1
        sheet_url[name] = sheet.url
    log.info("[TOOL-`count_distribution_transaction`] Tool executed successfully")
    return ToolResult(
        result=distribution,
        reference=sheet_url
    )


@tool
def count_total_amount(sheet_name: str,
                      from_date: str = None, to_date: str = None,
                      from_amount: float = None, to_amount: float = None,
                      transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                      payment_method: Literal["Thẻ", "Tiền mặt"] | None = None) -> ToolResult:
    """
    Count the total amount of transactions from a worksheet with optional filtering.
    
    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        from_date (str, optional): Start date for filtering in 'DD-MM-YYYY' format.
        to_date (str, optional): End date for filtering in 'DD-MM-YYYY' format.
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).
    
    Returns:
        float: The total amount of transactions that match the filter criteria.
    """
    log.info("[TOOL-`count_total_amount`] Execute tool")
    sheet = get_client().worksheet(title=sheet_name)
    all_transaction = sheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    result = sum([convert_amount_to_float(transaction[1]) for transaction in filtered_transaction])

    log.info("[TOOL-`count_total_amount`] Tool executed successfully")
    return ToolResult(
        result=result,
        reference={sheet_name: sheet.url}
    )


@tool
def count_total_amount_multi_sheet(sheet_names: List[str],
                      from_date: str = None, to_date: str = None,
                      from_amount: float = None, to_amount: float = None,
                      transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                      payment_method: Literal["Thẻ", "Tiền mặt"] | None = None) -> ToolResult:
    """
    Count the total amount of transactions from multiple worksheets with optional filtering.
    
    Args:
        sheet_names (List[str]): List of worksheet titles to read transactions from. Each title must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        from_date (str, optional): Start date for filtering in 'DD-MM-YYYY' format.
        to_date (str, optional): End date for filtering in 'DD-MM-YYYY' format.
        from_amount (float, optional): Minimum transaction amount.
        to_amount (float, optional): Maximum transaction amount.
        transaction_type (Literal["Chi", "Nhận"] | None): Type of transaction ("Nhận" or "Chi").
        description (str, optional): Partial description to match.
        payment_method (Literal["Thẻ", "Tiền mặt"] | None): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).
    
    Returns:
        Dict[str, float]: A dictionary where keys are sheet names and values are the total amounts of transactions that match the filter criteria for each sheet.
    """
    log.info("[TOOL-`count_total_amount_multi_sheet`] Execute tool")
    result = dict()
    sheet_url = dict()
    for sheet_name in sheet_names:
        sheet = get_client().worksheet(title=sheet_name)
        all_transaction = sheet.get_all_values(range_name=RANGE)
        all_transaction = fill_date(all_transaction)
        filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
        result[sheet_name] = sum([convert_amount_to_float(transaction[1]) for transaction in filtered_transaction])
        sheet_url[sheet_name] = sheet.url
    
    log.info("[TOOL-`count_total_amount_multi_sheet`] Tool executed successfully")
    return ToolResult(
        result=result,
        reference=sheet_url
    )

