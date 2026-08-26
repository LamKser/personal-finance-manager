from typing import List
from operator import itemgetter
from datetime import datetime


OLD_DATE_FORMAT = "%a, %d-%m-%Y" # Ex: Mon, 17-08-2026
NEW_DATE_FORMAT = "%Y-%m-%d" # Ex: 2026-08-17


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
            float_amount = float(row[1][:-2].replace(',', ''))
            if from_amount > float_amount:
                continue

        if to_amount:
            float_amount = float(row[1][:-2].replace(',', ''))
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
    result = list(itemgetter(*filter_index)(transaction))
    return result


def fill_date(rows: List[List[str]]) -> List[List[str]]:
    last_date = ""
    for row in rows:
        last_date = row[0] or last_date
        row[0] = last_date
    return rows
