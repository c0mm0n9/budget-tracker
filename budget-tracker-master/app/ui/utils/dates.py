from __future__ import annotations

from datetime import date as py_date
from datetime import datetime, time

from PyQt6.QtCore import QDate


def qdate_to_date(qd: QDate) -> py_date:
    return py_date(qd.year(), qd.month(), qd.day())


def date_to_qdate(d: py_date) -> QDate:
    return QDate(d.year, d.month, d.day)


def qdate_to_timestamp(qd: QDate) -> int:
    """
    Convert a *date-only* QDate into a unix timestamp at local midnight.
    """
    d = qdate_to_date(qd)
    local_dt = datetime.combine(d, time.min)
    return int(local_dt.timestamp())


def timestamp_to_qdate(ts: int) -> QDate:
    """
    Convert a unix timestamp into a *date-only* QDate (local timezone).
    """
    dt = datetime.fromtimestamp(ts)
    return QDate(dt.year, dt.month, dt.day)

