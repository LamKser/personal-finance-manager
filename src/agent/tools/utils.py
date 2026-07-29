from typing import Dict

from langchain_core.tools import tool

from src.agent.tools.date_time import get_today_datetime


@tool
def extract_transaction_information(description: str, amount: float, transaction_type: str, payment_method: str) -> Dict:
    """Extract structured transaction information from user input.

    Creates a transaction record using the extracted information and assigns the current date and time as the transaction timestamp.
    The `description` field should be summarized to provide a clear and concise description of the transaction. It does not include any personal information and amount.
    The `transaction_type` field should be either "Thu" or "Chi". If the transaction is income, use "Thu". If the transaction is expense, use "Chi".
    The `payment_method` field should be either "Thẻ" or "Tiền mặt". If the transaction is made by online payment, card or other digital method, use "Thẻ". If the transaction is made by cash, use "Tiền mặt".
    In case if some fields is missing, they will be set to::
    - `description`: "Unknown"
    - `amount`: -1
    - `transaction_type`: '' (Empty string)
    - `payment_method`: '' (Empty string)

    Args:
        description (str): A brief description of the transaction.
        amount (float): The transaction amount.
        transaction_type (str): The type of transaction ("Thu" or "Chi").
        payment_method (str): The method used to make the payment ("Thẻ" or "Tiền mặt")

    Returns:
        A dictionary containing the transaction information with the following keys:
            - date: The current date and time.
            - description: The transaction description.
            - amount: The transaction amount.
            - transaction_type: The transaction type.
            - payment_method: The payment method
    """
    date = get_today_datetime()
    return {
        "date": date,
        "description": description,
        "amount": amount,
        "transaction_type": transaction_type,
        "payment_method": payment_method
    }


