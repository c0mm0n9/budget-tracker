from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QComboBox, QDateEdit, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.storage.transaction_model import TransactionModel
from app.ui.controllers.app_controller import AppController
from app.ui.design.components import StandardDialog
from app.ui.utils.dates import qdate_to_timestamp, timestamp_to_qdate


class TransactionDialog(StandardDialog):
    def __init__(
        self,
        controller: AppController,
        *,
        transaction: TransactionModel | None = None,
        parent: QWidget | None = None,
    ) -> None:
        title = "Edit Transaction" if transaction else "Add Transaction"
        super().__init__(title=title, parent=parent)
        if transaction is None:
            self.set_save_text("Create")

        self._controller = controller
        self._transaction = transaction

        self._date_edit = QDateEdit(self)
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        self._date_edit.setDate(timestamp_to_qdate(transaction.timestamp) if transaction else QDate.currentDate())

        self._category_edit = QLineEdit(self)
        self._category_edit.setPlaceholderText("e.g. Groceries")
        self._tag_edit = QLineEdit(self)
        self._tag_edit.setPlaceholderText("Optional tag")

        self._type_edit = QComboBox(self)
        self._type_edit.addItems(["Expense (-)", "Income (+)"])

        self._amount_edit = QLineEdit(self)
        self._amount_edit.setPlaceholderText("0.00")
        self._amount_edit.setValidator(QDoubleValidator(0.0, 10_000_000.0, 2, self))

        if transaction:
            self._category_edit.setText(transaction.category)
            self._tag_edit.setText(transaction.tag)
            self._amount_edit.setText(f"{abs(transaction.amount):.2f}")
            self._type_edit.setCurrentText("Income (+)" if transaction.amount >= 0 else "Expense (-)")

        # Layout
        self.content_layout.addWidget(self._field_label_pair("Date", self._date_edit))
        self.content_layout.addWidget(
            self._field_label_pair("Category", self._category_edit)
        )
        self.content_layout.addWidget(self._field_label_pair("Tag", self._tag_edit))
        self.content_layout.addWidget(self._field_label_pair("Type", self._type_edit))
        self.content_layout.addWidget(
            self._field_label_pair("Amount", self._amount_edit)
        )

        # Default Save action
        self.save_button.clicked.connect(self._on_submit)

    def _field_label_pair(self, label: str, widget: QWidget) -> QWidget:
        row = QWidget(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        row.setLayout(layout)

        lbl = QLabel(label)
        lbl.setProperty("muted", "true")
        lbl.setStyleSheet("font-size: 12.5px; font-weight: 600;")
        layout.addWidget(lbl)
        layout.addWidget(widget)
        return row

    def _on_submit(self) -> None:
        self.clear_error()

        d = self._date_edit.date()
        category = self._category_edit.text().strip()
        tag = self._tag_edit.text().strip()

        amount_text = self._amount_edit.text().strip()
        if not category:
            self.show_error("Category is required.")
            return
        if not amount_text:
            self.show_error("Amount is required.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            self.show_error("Amount must be a valid number.")
            return

        if self._type_edit.currentText() == "Expense (-)":
            amount = -abs(amount)
        else:
            amount = abs(amount)

        # Convert date-only QDate to local midnight timestamp.
        timestamp = qdate_to_timestamp(d)

        if self._transaction is None:
            # Generate a new id (max+1).
            existing = self._controller.transactions_manager.get_all_transactions()
            new_id = max((tx.id for tx in existing), default=0) + 1
            model = TransactionModel(
                id=new_id,
                timestamp=timestamp,
                category=category,
                amount=amount,
                tag=tag,
            )
            self._controller.transactions_manager.create_transaction(model)
        else:
            model = TransactionModel(
                id=self._transaction.id,
                timestamp=timestamp,
                category=category,
                amount=amount,
                tag=tag,
            )
            updated = self._controller.transactions_manager.update_transaction(
                self._transaction.id, model
            )
            if updated is None:
                self.show_error("Failed to update transaction (not found).")
                return

        self.accept()

