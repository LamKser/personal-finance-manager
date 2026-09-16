from typing import List, Tuple
from operator import itemgetter
from datetime import datetime
from sys import maxsize


OLD_DATE_FORMAT = "%a, %d-%m-%Y" # Ex: Mon, 17-08-2026
NEW_DATE_FORMAT = "%d-%m-%Y" # Ex: 17-08-2026
BIG_INTEGER = maxsize


def filter_transaction(transaction: List[List[str]],
                       from_date: str=None, to_date: str=None,
                       from_amount: float=None, to_amount: float=None, 
                       transaction_type: str=None, description: str=None, payment_method: str=None
                       ) -> List[List[str]]:
    filter_index = list()
    filter_index.append(0) # Keep headers
    for index, row in enumerate(transaction[1:], start = 1):
        # "Ngày" column
        if from_date:
            new_date = datetime.strptime(row[0], OLD_DATE_FORMAT).strftime(NEW_DATE_FORMAT)

            if from_date > new_date:
                continue

        if to_date:
            new_date = datetime.strptime(row[0], OLD_DATE_FORMAT).strftime(NEW_DATE_FORMAT)
            if to_date < new_date:
                continue

        # "Số tiền" column
        if from_amount:
            float_amount = convert_amount_to_float(row[1])
            if from_amount > float_amount:
                continue

        if to_amount:
            float_amount = convert_amount_to_float(row[1])
            if to_amount < float_amount:
                continue

        # "Chi/Nhận" column
        if transaction_type and row[2] != transaction_type:
            continue

        # "Mô tả" column
        if description:
            pass # TODO

        # "Hình thức" column
        if payment_method and row[4] != payment_method:
            continue

        filter_index.append(index)
    if len(filter_index) == 1:
        filter_index = [filter_index]
    result = list(itemgetter(*filter_index)(transaction))
    return result


def fill_date(rows: List[List[str]]) -> List[List[str]]:
    last_date = ""
    for row in rows:
        last_date = row[0] or last_date
        row[0] = last_date
    return rows


def has_empty_cell(values: List[str]) -> bool:
    values.pop(3) # Remove column "Mô tả"
    return not all(value.strip() for value in values)


def get_index_empty_cell_by_date(values: List[List[str]], date: str) -> int:
    new_date = datetime.strptime(date, "%m-%d-%Y").strftime(NEW_DATE_FORMAT)
    for index, value in enumerate(values, start=0):
        if index == 0: continue
        get_date = datetime.strptime(value[0], "%a, %d-%m-%Y").strftime(NEW_DATE_FORMAT)
        if has_empty_cell(value.copy()) or (new_date < get_date): return index - 1
    return len(values) - 1


def convert_amount_to_float(amount: str) -> float:
    return float(amount[:-2].replace(',', ''))


def get_merge_range_date(transaction: List[List[str]], date: str) -> Tuple[int, int]:
    if len(transaction) == 2: return 0, 0
    new_date = datetime.strptime(date, "%m-%d-%Y").strftime(OLD_DATE_FORMAT)
    start_row, end_row = 0, 0
    for index, row in enumerate(transaction[1:], start=2):
        if row[0] == new_date:
            if not start_row:
                start_row = index
            end_row = index
    return start_row, end_row

def get_max_amount_index(transaction: List[List[str]]) -> List[int]:
    max_amount = -1
    result = []

    for idx, row in enumerate(transaction[1:], start=1):
        amount = convert_amount_to_float(row[1])

        if amount > max_amount:
            max_amount = amount
            result = [idx]
        elif amount == max_amount:
            result.append(idx)
    return result

def get_min_amount_index(transaction: List[List[str]]) -> List[int]:
    min_amount = BIG_INTEGER
    result = []

    for idx, row in enumerate(transaction[1:], start=1):
        amount = convert_amount_to_float(row[1])

        if amount < min_amount:
            min_amount = amount
            result = [idx]
        elif amount == min_amount:
            result.append(idx)
    return result
