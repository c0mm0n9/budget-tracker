from app.storage.transaction_model import TransactionModel
from datetime import datetime, timedelta


def top_week(
    transactions: list[TransactionModel],
    limit: int = 5,
) -> list[TransactionModel]:
    """
    Get the top week.
    """
    return sorted(transactions, key=lambda x: x.amount, reverse=True)[:limit]


def top_month(
    transactions: list[TransactionModel],
    limit: int = 5,
    start: datetime = datetime.now().replace(day=1),
    end: datetime = datetime.now().replace(day=1) + timedelta(days=31),
) -> list[TransactionModel]:
    """
    Get the top month.
    """
    return [
        transaction
        for transaction in transactions
        if start <= datetime.fromtimestamp(transaction.timestamp) <= end
    ][:limit]


def top_year(
    transactions: list[TransactionModel],
    limit: int = 5,
    start: datetime = datetime.now().replace(day=1, month=1),
    end: datetime = datetime.now().replace(day=1, month=1) + timedelta(days=365),
) -> list[TransactionModel]:
    """
    Get the top year.
    """
    return [
        transaction
        for transaction in transactions
        if start <= datetime.fromtimestamp(transaction.timestamp) <= end
    ][:limit]
