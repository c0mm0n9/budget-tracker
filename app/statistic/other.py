from app.storage.transaction_model import TransactionModel
from datetime import datetime, timedelta


def transactions_this_month(
    transactions: list[TransactionModel]
    ) -> list[TransactionModel]:
    """
    Get all transactions this month.
    """
    start_of_month = datetime.now().replace(day=1)
    end_of_month = start_of_month + timedelta(days=31)
    return [
        transaction for transaction in transactions 
        if start_of_month <= datetime.fromtimestamp(transaction.timestamp) <= end_of_month
    ]

def transactions_this_week(
    transactions: list[TransactionModel]
    ) -> list[TransactionModel]:
    """
    Get all transactions this week.
    """
    start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
    end_of_week = start_of_week + timedelta(days=7)
    return [
        transaction for transaction in transactions 
        if start_of_week <= datetime.fromtimestamp(transaction.timestamp) <= end_of_week
    ]

def average_this_month(transactions: list[TransactionModel]) -> float:
    """
    Calculate the average spending this month.
    """
    transactions_this_month = transactions_this_month(transactions)
    return sum(
        transaction.amount for transaction in transactions_this_month
    ) / len(transactions_this_month)


def average_this_week(transactions: list[TransactionModel]) -> float:
    """
    Calculate the average spending this week.
    """
    transactions_this_week = transactions_this_week(transactions)   
    return sum(
        transaction.amount for transaction in transactions_this_week
    ) / len(transactions_this_week)