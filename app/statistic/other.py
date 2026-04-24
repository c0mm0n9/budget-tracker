from datetime import datetime, timedelta

from app.storage.transaction_model import TransactionModel


def _start_of_month(now: datetime) -> datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _start_of_week(now: datetime) -> datetime:
    start = now - timedelta(days=now.weekday())
    return start.replace(hour=0, minute=0, second=0, microsecond=0)


def transactions_this_month(
    transactions: list[TransactionModel],
    now: datetime | None = None,
    ) -> list[TransactionModel]:
    """
    Get all transactions this month.
    """
    now = now or datetime.now()
    start_of_month = _start_of_month(now)
    next_month = (
        start_of_month.replace(day=28) + timedelta(days=4)
    ).replace(day=1)
    return [
        transaction for transaction in transactions 
        if start_of_month <= datetime.fromtimestamp(transaction.timestamp) < next_month
    ]

def transactions_this_week(
    transactions: list[TransactionModel],
    now: datetime | None = None,
    ) -> list[TransactionModel]:
    """
    Get all transactions this week.
    """
    now = now or datetime.now()
    start_of_week = _start_of_week(now)
    end_of_week = start_of_week + timedelta(days=7)
    return [
        transaction for transaction in transactions 
        if start_of_week <= datetime.fromtimestamp(transaction.timestamp) < end_of_week
    ]

def average_this_month(
    transactions: list[TransactionModel],
    now: datetime | None = None,
) -> float:
    """
    Calculate the average spending this month.
    """
    month_txs = transactions_this_month(transactions, now=now)
    if not month_txs:
        return 0.0
    return sum(transaction.amount for transaction in month_txs) / len(month_txs)


def average_this_week(
    transactions: list[TransactionModel],
    now: datetime | None = None,
) -> float:
    """
    Calculate the average spending this week.
    """
    week_txs = transactions_this_week(transactions, now=now)
    if not week_txs:
        return 0.0
    return sum(transaction.amount for transaction in week_txs) / len(week_txs)
