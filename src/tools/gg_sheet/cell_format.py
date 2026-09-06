from typing import Dict


FORMAT_DATE = {"type": "DATE", "pattern": "ddd, dd-mm-yyyy"}
FORMAT_CURRENCY = {"type": "CURRENCY", "pattern": '#,##0[$ ₫]'}

# =================================== Style ===================================
def transaction_condition_style(value: str, sheet_id: int,
                                start_row_index: str, end_row_index: str,
                                start_column_index: str, end_column_index: str) -> Dict:
    color = {
        "Thu": {"red": 0, "green": 1, "blue": 0,},
        "Chi": {"red": 1, "green": 0, "blue": 0}
    }

    index = 0
    if value == "Thu": index = 1
    style = {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": start_row_index,
                    "endRowIndex": end_row_index,
                    "startColumnIndex": start_column_index,
                    "endColumnIndex": end_column_index,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [{"userEnteredValue": value}],
                    },
                    "format": {
                        "backgroundColor": color[value]
                    },
                },
            },
            "index": index,
        }
    }
    return style


def payment_condition_style(value: str, sheet_id: int,
                            start_row_index: str, end_row_index: str,
                            start_column_index: str, end_column_index: str) -> Dict:
    color = {
        "Thẻ": {"red": 0, "green": 1, "blue": 0,},
        "Tiền mặt": {"red": 1, "green": 1, "blue": 1}
    }

    index = 0
    if value == "Tiền mặt": index = 1
    style = {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": start_row_index,
                    "endRowIndex": end_row_index,
                    "startColumnIndex": start_column_index,
                    "endColumnIndex": end_column_index,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [{"userEnteredValue": value}],
                    },
                    "format": {
                        "backgroundColor": color[value]
                    },
                },
            },
            "index": index,
        }
    }
    return style