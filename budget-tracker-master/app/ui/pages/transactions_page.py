from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from app.ui.controllers.app_controller import AppController
from app.ui.design.components import (
    Card,
    EmptyState,
    PrimaryButton,
    SectionHeader,
    style_message_box,
)
from app.ui.dialogs.transaction_dialog import TransactionDialog
from app.ui.utils.formatters import format_currency


class TransactionsPage(QWidget):
    def __init__(self, controller: AppController | None = None) -> None:
        super().__init__()
        self._controller = controller or AppController()

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        root.addWidget(SectionHeader("Transactions"))

        # Header row (add action only)
        header = QWidget(self)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        header.setLayout(header_layout)

        header_layout.addStretch(1)

        self._add_btn = PrimaryButton("Add Transaction")
        self._add_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self._add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        root.addWidget(header)

        # Card with table / empty state
        card = Card(self)
        card_layout = card.content_layout
        card_layout.setContentsMargins(0, 0, 0, 0)

        self._empty_state = EmptyState(
            "No transactions found.",
            action_text="Add Transaction",
            action_callback=self._open_add_dialog,
        )

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["DATE", "CATEGORY", "TAG", "AMOUNT", "ACTIONS"])
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        header_view: QHeaderView = self._table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header_view.setMinimumSectionSize(80)

        card_layout.addWidget(self._table)
        card_layout.addWidget(self._empty_state)
        self._empty_state.setVisible(False)

        root.addWidget(card, 1)
        self.setLayout(root)

        self._refresh_table()

    def _open_add_dialog(self) -> None:
        dialog = TransactionDialog(self._controller, parent=self)
        from PyQt6.QtWidgets import QDialog

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.refresh()
            self._refresh_table()

    def _open_edit_dialog(self, tx) -> None:
        dialog = TransactionDialog(self._controller, transaction=tx, parent=self)
        from PyQt6.QtWidgets import QDialog

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.refresh()
            self._refresh_table()

    def _confirm_delete(self, tx) -> bool:
        msg = QMessageBox(self)
        style_message_box(msg)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Delete transaction?")
        msg.setText(f"Delete this transaction for {tx.category} on {datetime.fromtimestamp(tx.timestamp).strftime('%Y-%m-%d')}?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        return msg.exec() == QMessageBox.StandardButton.Yes

    def _delete_transaction(self, tx) -> None:
        if not self._confirm_delete(tx):
            return
        self._controller.transactions_manager.delete_transaction(tx.id)
        self._controller.refresh()
        self._refresh_table()

    def _refresh_table(self) -> None:
        filtered = list(self._controller.transactions_manager.get_all_transactions())

        filtered.sort(key=lambda x: x.timestamp, reverse=True)

        self._table.setRowCount(len(filtered))

        if not filtered:
            self._table.setVisible(False)
            self._empty_state.setVisible(True)
            return

        self._table.setVisible(True)
        self._empty_state.setVisible(False)

        for row, tx in enumerate(filtered):
            date_item = QTableWidgetItem(datetime.fromtimestamp(tx.timestamp).strftime("%Y-%m-%d"))
            cat_item = QTableWidgetItem(str(tx.category))
            tag_item = QTableWidgetItem(str(tx.tag))
            amount_item = QTableWidgetItem(format_currency(float(tx.amount)))

            # Store raw amount for potential future sorting/filtering.
            amount_item.setData(Qt.ItemDataRole.UserRole, float(tx.amount))

            self._table.setItem(row, 0, date_item)
            self._table.setItem(row, 1, cat_item)
            self._table.setItem(row, 2, tag_item)
            self._table.setItem(row, 3, amount_item)

            action_cell = QWidget(self._table)
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)
            action_cell.setLayout(layout)

            edit_btn = QPushButton("Edit", action_cell)
            edit_btn.setProperty("variant", "neutral")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda _checked=False, t=tx: self._open_edit_dialog(t))

            del_btn = QPushButton("Delete", action_cell)
            del_btn.setProperty("variant", "danger")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _checked=False, t=tx: self._delete_transaction(t))

            for b in (edit_btn, del_btn):
                b.setFixedHeight(28)
                layout.addWidget(b)
                b.style().unpolish(b)
                b.style().polish(b)

            self._table.setCellWidget(row, 4, action_cell)



