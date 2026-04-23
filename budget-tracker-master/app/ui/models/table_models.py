from __future__ import annotations

from typing import Any, Callable, Sequence

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt


class GenericTableModel(QAbstractTableModel):
    """
    Generic display-only table model.

    Action columns are intentionally not handled here; pages can still use
    QWidget-based cell actions when needed.
    """

    def __init__(
        self,
        rows: Sequence[Any],
        headers: Sequence[str],
        value_getter: Callable[[Any, int], Any],
    ) -> None:
        super().__init__()
        self._rows = list(rows)
        self._headers = list(headers)
        self._value_getter = value_getter

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._rows)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._headers)

    def data(
        self,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        row = self._rows[index.row()]
        return self._value_getter(row, index.column())

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return str(section + 1)


class TransactionsTableModel(GenericTableModel):
    def __init__(self, transactions: Sequence[Any]) -> None:
        from datetime import datetime

        from app.ui.utils.formatters import format_currency

        headers = ["DATE", "CATEGORY", "TAG", "AMOUNT"]

        def value_getter(tx: Any, col: int) -> Any:
            if col == 0:
                return datetime.fromtimestamp(tx.timestamp).strftime("%Y-%m-%d")
            if col == 1:
                return tx.category
            if col == 2:
                return tx.tag
            if col == 3:
                return format_currency(float(tx.amount))
            return ""

        super().__init__(transactions, headers, value_getter)


class BudgetsTableModel(GenericTableModel):
    def __init__(self, budgets: Sequence[Any]) -> None:
        from app.ui.utils.formatters import format_currency

        headers = ["NAME", "START", "END", "AMOUNT"]

        def value_getter(b: Any, col: int) -> Any:
            if col == 0:
                return b.name
            if col == 1:
                return b.start.strftime("%Y-%m-%d")
            if col == 2:
                return b.end.strftime("%Y-%m-%d")
            if col == 3:
                return format_currency(float(b.amount))
            return ""

        super().__init__(budgets, headers, value_getter)


class RulesTableModel(GenericTableModel):
    def __init__(self, rules: Sequence[Any]) -> None:
        headers = ["NAME", "RULE", "MESSAGE"]

        def value_getter(r: Any, col: int) -> Any:
            if col == 0:
                return r.name
            if col == 1:
                return r.rule
            if col == 2:
                return r.message or ""
            return ""

        super().__init__(rules, headers, value_getter)

