

from typing import Literal
from logging import getLogger

log = getLogger(__name__)

from langchain_core.tools import tool

from src.schema import ToolResult
from src.tools.gg_sheet.client import get_client
from src.tools.gg_sheet.utils.utils import fill_date, has_empty_cell, get_index_empty_cell_by_date, get_merge_range_date
from src.tools.gg_sheet.cell_format import transaction_condition_style, payment_condition_style
from src.tools.gg_sheet.cell_format import FORMAT_CURRENCY, FORMAT_DATE


RANGE = "A:E"


@tool
def add_new_transaction(sheet_name: str,
                    date: str,
                    amount: float,
                    transaction_type: Literal["Chi", "Nhận"],
                    description: str,
                    payment_method: Literal["Thẻ", "Tiền mặt"]) -> ToolResult:
    """Add a new transaction record to the specified worksheet.

    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        date (str): Date of transaction in 'MM-DD-YYYY' format.
        amount (float): Transaction amount.
        transaction_type (Literal["Chi", "Nhận"]): Type of transaction ("Nhận" or "Chi").
        description (str): Summary of transaction.
        payment_method (Literal["Thẻ", "Tiền mặt"]): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns: 
        None: The transaction is added to the worksheet.
    """
    log.info("[TOOL] - `add_new_transaction` - Execute tool")
    worksheet = get_client().worksheet(title=sheet_name)
    all_transaction = worksheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)

    index_add_cell = get_index_empty_cell_by_date(all_transaction, date)
    log.debug("[TOOL] - `add_new_transaction` - Row found: %d - Data: %s", index_add_cell + 1, all_transaction[index_add_cell])
    check_empty_row = has_empty_cell(all_transaction[index_add_cell])
    log.debug("[TOOL] - `add_new_transaction` - Row %d is empty: %s", index_add_cell  + 1, check_empty_row)
    index_add_cell += 2
    
    if not check_empty_row:
        worksheet.insert_row([], index=index_add_cell)
        log.debug("[TOOL] - `add_new_transaction` - Insert empty row below row %d", index_add_cell)
    worksheet.update(
        [[date, amount, transaction_type, description, payment_method]],
        f"A{index_add_cell}:E{index_add_cell}",
        raw=False
    )
    log.debug("[TOOL] - `add_new_transaction` - Added new data at row %d - New data: %s", index_add_cell, [date, amount, transaction_type, description, payment_method])
    log.info("[TOOL] - `add_new_transaction` - Transaction display format")
    # Format date
    worksheet.format(f"A{index_add_cell}", {"numberFormat": FORMAT_DATE})
    log.debug("[TOOL] - `add_new_transaction` - Formatted `date`")

    # Format currency
    worksheet.format(f"B{index_add_cell}", {"numberFormat": FORMAT_CURRENCY})
    log.debug("[TOOL] - `add_new_transaction` - Formatted `currency`")

    # Format transaction type style - column C (2-3)
    get_client().batch_update({
        "requests": [
            transaction_condition_style("Nhận", worksheet.id, index_add_cell-1, index_add_cell, 2, 3),
            transaction_condition_style("Chi", worksheet.id, index_add_cell-1, index_add_cell, 2, 3)
        ]
    })
    log.debug("[TOOL] - `add_new_transaction` - Formatted `transaction_type`")

    # # Format payment method style - column E (4-5)
    get_client().batch_update({
        "requests": [
            payment_condition_style("Thẻ", worksheet.id, index_add_cell-1, index_add_cell, 4, 5),
            payment_condition_style("Tiền mặt", worksheet.id, index_add_cell-1, index_add_cell, 4, 5)
        ]
    })
    log.debug("[TOOL] - `add_new_transaction` - Formatted `payment_method`")

    # Merge date cells
    worksheet = get_client().worksheet(title=sheet_name)
    all_transaction = worksheet.get_all_values(range_name=RANGE)
    start_row, end_row = get_merge_range_date(all_transaction, date)
    if start_row and end_row:
        worksheet.merge_cells(f"A{start_row}:A{end_row}", merge_type="MERGE_ALL")
        log.debug("[TOOL] - `add_new_transaction` - Merged date cells from row %d to %d", start_row, end_row)
    
    log.info("[TOOL] - `add_new_transaction` - Tool executed successfully")
    return ToolResult(
        result=f"Add new transaction ({date} | {amount} | {transaction_type} | {description} | {payment_method})",
        reference={sheet_name: worksheet.url}
    )


# @tool
# def add_new_sheet():
#     pass


# @tool
# def add_multi_new_sheets():
#     pass


# @tool
# def add_new_spreadsheet(spreadsheet_name: str):
#     pass

