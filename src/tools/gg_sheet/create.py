from typing import Literal
from logging import getLogger

log = getLogger(__name__)

from langchain_core.tools import tool

from src.tools.gg_sheet.client import client
from src.tools.gg_sheet.utils import fill_date, has_empty_cell, get_index_empty_cell_by_date
from src.tools.gg_sheet.cell_format import FORMAT_CURRENCY, FORMAT_DATE, transaction_condition_style, payment_condition_style


RANGE = "A:E"


@tool
def add_new_transaction(sheet_name: str,
                    date: str,
                    amount: float,
                    transaction_type: Literal["Chi", "Nhận"],
                    description: str,
                    payment_method: Literal["Thẻ", "Tiền mặt"]) -> None:
    """Add a new transaction record to the specified worksheet.

    Args:
        sheet_name (str): Title of the worksheet to read transactions from. Must be either "Tổng hợp" (summary) or "Tháng X", where X is the month number (1-12).
        date (str): Date of transaction in 'MM-DD-YYYY' format.
        amount (float): Transaction amount.
        transaction_type (Literal["Chi", "Nhận"]): Type of transaction ("Nhận" or "Chi").
        description (str): Summary of transaction. (ALWAYS HAVE. ONLY "Không biết" for unknown transaction)
        payment_method (Literal["Thẻ", "Tiền mặt"]): Payment method used ("Thẻ" - made by online payment, card or other digital method, or "Tiền mặt" - made by cash).

    Returns: 
        None: The transaction is added to the worksheet.
    """
    log.info("[TOOL] Excute tool `add_new_transaction`")
    worksheet = client.worksheet(title=sheet_name)
    all_transaction = worksheet.get_all_values(range_name=RANGE)
    all_transaction = fill_date(all_transaction)

    index_add_cell = get_index_empty_cell_by_date(all_transaction, date)
    check_empty_row = has_empty_cell(all_transaction[index_add_cell])
    index_add_cell += 1
    if not check_empty_row:
        worksheet.insert_row([], index=index_add_cell)
    worksheet.update(
        [[date, amount, transaction_type, description, payment_method]],
        f"A{index_add_cell}:E{index_add_cell}",
        raw=False
    )

    # Format date
    worksheet.format(f"A{index_add_cell}", {"numberFormat": FORMAT_DATE})

    # Format currency
    worksheet.format(f"B{index_add_cell}", {"numberFormat": FORMAT_CURRENCY})

    # Format transaction type style - column C (3-4)
    client.batch_update({
        "requests": [
            transaction_condition_style("Nhận", worksheet.id, index_add_cell-1, index_add_cell, 2, 3),
            transaction_condition_style("Chi", worksheet.id, index_add_cell-1, index_add_cell, 2, 3)
        ]
    })

    # # Format payment method style - column E (4-5)
    client.batch_update({
        "requests": [
            payment_condition_style("Thẻ", worksheet.id, index_add_cell-1, index_add_cell, 4, 5),
            payment_condition_style("Tiền mặt", worksheet.id, index_add_cell-1, index_add_cell, 4, 5)
        ]
    })

    log.info("[TOOL-DONE] Excuted tool `add_new_transaction`")
    return


# @tool
# def add_multi_new_transactions():
#     pass

# @tool
# def add_new_sheet():
#     pass


# @tool
# def add_multi_new_sheets():
#     pass
