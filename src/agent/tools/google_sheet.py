from typing import Dict

from langchain_core.tools import tool

from src.agent.tools.date_time import get_today_datetime


@tool
def extract_transaction_information(description: str, amount: float, transaction_type: str, payment_method: str) -> Dict:
    """Extract structured transaction information from user input.

    Creates a transaction record using the extracted information and assigns the current date and time as the transaction timestamp.
    In case if user input does not contain all information or missing some fields, the missing fields will be set to:
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
