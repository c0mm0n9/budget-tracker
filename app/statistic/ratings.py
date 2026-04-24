from datetime import datetime, timedelta

from app.storage.transaction_model import TransactionModel


def _start_of_week(now: datetime) -> datetime:
    start = now - timedelta(days=now.weekday())
    return start.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_month(now: datetime) -> datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _start_of_year(now: datetime) -> datetime:
    return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def _next_month_start(start_of_month: datetime) -> datetime:
    return (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)


def _next_year_start(start_of_year: datetime) -> datetime:
    return start_of_year.replace(year=start_of_year.year + 1)


def _top_transactions(
    transactions: list[TransactionModel],
    *,
    start: datetime,
    end: datetime,
    limit: int,
) -> list[TransactionModel]:
    filtered = [
        transaction
        for transaction in transactions
        if start <= datetime.fromtimestamp(transaction.timestamp) < end
    ]
    return sorted(filtered, key=lambda x: abs(float(x.amount)), reverse=True)[:limit]


def top_week(
    transactions: list[TransactionModel],
    limit: int = 5,
    now: datetime | None = None,
) -> list[TransactionModel]:
    """
    Get the top transactions from the current week.
    """
    now = now or datetime.now()
    start = _start_of_week(now)
    end = start + timedelta(days=7)
    return _top_transactions(transactions, start=start, end=end, limit=limit)


def top_month(
    transactions: list[TransactionModel],
    limit: int = 5,
    now: datetime | None = None,
) -> list[TransactionModel]:
    """
    Get the top transactions from the current month.
    """
    now = now or datetime.now()
    start = _start_of_month(now)
    end = _next_month_start(start)
    return _top_transactions(transactions, start=start, end=end, limit=limit)


def top_year(
    transactions: list[TransactionModel],
    limit: int = 5,
    now: datetime | None = None,
) -> list[TransactionModel]:
    """
    Get the top transactions from the current year.
    """
    now = now or datetime.now()
    start = _start_of_year(now)
    end = _next_year_start(start)
    return _top_transactions(transactions, start=start, end=end, limit=limit)
