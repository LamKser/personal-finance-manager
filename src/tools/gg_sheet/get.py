


from typing import List, Literal
from operator import itemgetter
from logging import getLogger

log = getLogger(__name__)

from langchain_core.tools import tool

from src.schema import ToolResult
from src.tools.gg_sheet.client import get_client
from src.tools.gg_sheet.utils.utils import fill_date, filter_transaction, get_max_amount_index, get_min_amount_index


RANGE = "A:E"


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
    log.info("[TOOL] - `get_transaction` - Execute tool")
    sheet = get_client().worksheet(title=sheet_name)
    all_transaction = sheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    log.info("[TOOL] - `get_transaction` - Tool executed successfully")
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
    log.info("[TOOL] - `get_transaction_multi_sheet` - Execute tool")
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
    log.info("[TOOL] - `get_transaction_multi_sheet` - Tool executed successfully")
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
    log.info("[TOOL] - `get_all_transactions` - Execute tool")
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
    log.info("[TOOL] - `get_all_transactions` - Tool executed successfully")
    return ToolResult(
        result=result,
        reference=sheet_url
    )


@tool
def get_max_amount(sheet_name: str,
                    from_date: str = None, to_date: str = None,
                    from_amount: float = None, to_amount: float = None,
                    transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                    payment_method: Literal["Thẻ", "Tiền mặt"] | None = None) -> List[List[str]]:
    """Retrieve transaction records with the HIGHEST amount from a worksheet with optional filtering.
    
    Fetches the cell values for the transaction details from the specified worksheet, applies filters based on the provided criteria and returns transactions with the HIGHEST amount.

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
        List[List[str]]: A list of transaction with the HIGHEST amount, where each row is a list of string cell values. The first row typically contains the header labels.
    """
    log.info("[TOOL] - `get_max_amount` - Execute tool")
    sheet = get_client().worksheet(title=sheet_name)
    all_transaction = sheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    max_indices = get_max_amount_index(filtered_transaction)
    log.info("[TOOL] - `get_max_amount` - Tool executed successfully")
    return ToolResult(
        result=list(itemgetter(*max_indices)(filtered_transaction)),
        reference={
            sheet_name: sheet.url
        }
    )


@tool
def get_min_amount(sheet_name: str,
                    from_date: str = None, to_date: str = None,
                    from_amount: float = None, to_amount: float = None,
                    transaction_type: Literal["Chi", "Nhận"] | None = None, description: str = None,
                    payment_method: Literal["Thẻ", "Tiền mặt"] | None = None):
    """Retrieve transaction records with the LOWEST amount from a worksheet with optional filtering.
    
    Fetches the cell values for the transaction details from the specified worksheet, applies filters based on the provided criteria and returns transactions with the LOWEST amount.

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
        List[List[str]]: A list of transaction with the LOWEST amount, where each row is a list of string cell values. The first row typically contains the header labels.
    """
    log.info("[TOOL] - `get_min_amount` - Execute tool")
    sheet = get_client().worksheet(title=sheet_name)
    all_transaction = sheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)
    filtered_transaction = filter_transaction(all_transaction, from_date, to_date, from_amount, to_amount, transaction_type, description, payment_method)
    max_indices = get_min_amount_index(filtered_transaction)
    log.info("[TOOL] - `get_min_amount` - Tool executed successfully")
    return ToolResult(
        result=list(itemgetter(*max_indices)(filtered_transaction)),
        reference={
            sheet_name: sheet.url
        }
    )
