from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QDate
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QDateEdit, QLineEdit, QLabel, QVBoxLayout, QWidget

from app.storage.budget_model import BudgetModel
from app.ui.controllers.app_controller import AppController
from app.ui.design.components import StandardDialog
from app.ui.utils.dates import qdate_to_timestamp, timestamp_to_qdate


class BudgetDialog(StandardDialog):
    def __init__(
        self,
        controller: AppController,
        *,
        budget: BudgetModel | None = None,
        parent: QWidget | None = None,
    ) -> None:
        title = "Edit Budget" if budget else "New Budget"
        super().__init__(title=title, parent=parent)
        if budget is None:
            self.set_save_text("Create")

        self._controller = controller
        self._budget = budget

        self._name_edit = QLineEdit(self)
        self._name_edit.setPlaceholderText("e.g. Food Budget")

        self._start_edit = QDateEdit(self)
        self._start_edit.setCalendarPopup(True)
        self._start_edit.setDisplayFormat("yyyy-MM-dd")

        self._end_edit = QDateEdit(self)
        self._end_edit.setCalendarPopup(True)
        self._end_edit.setDisplayFormat("yyyy-MM-dd")

        self._amount_edit = QLineEdit(self)
        self._amount_edit.setPlaceholderText("0.00")
        self._amount_edit.setValidator(QDoubleValidator(0.0, 10_000_000.0, 2, self))

        if budget:
            self._name_edit.setText(budget.name)
            self._start_edit.setDate(timestamp_to_qdate(int(budget.start.timestamp())))
            self._end_edit.setDate(timestamp_to_qdate(int(budget.end.timestamp())))
            self._amount_edit.setText(f"{budget.amount:.2f}")
        else:
            today = QDate.currentDate()
            self._start_edit.setDate(today)
            self._end_edit.setDate(today.addDays(30))

        self.content_layout.addWidget(self._field_label_pair("Name", self._name_edit))
        self.content_layout.addWidget(
            self._field_label_pair("Start Date", self._start_edit)
        )
        self.content_layout.addWidget(self._field_label_pair("End Date", self._end_edit))
        self.content_layout.addWidget(
            self._field_label_pair("Amount", self._amount_edit)
        )

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

        name = self._name_edit.text().strip()
        amount_text = self._amount_edit.text().strip()

        start_ts = qdate_to_timestamp(self._start_edit.date())
        end_ts = qdate_to_timestamp(self._end_edit.date())
        start_dt = datetime.fromtimestamp(start_ts)
        end_dt = datetime.fromtimestamp(end_ts)

        if not name:
            self.show_error("Budget name is required.")
            return
        if not amount_text:
            self.show_error("Amount is required.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            self.show_error("Amount must be a valid number.")
            return

        if start_dt > end_dt:
            self.show_error("Start date must be before or equal to end date.")
            return

        if self._budget is None:
            existing = self._controller.budgets_manager.get_all_budgets()
            new_id = max((b.id for b in existing), default=0) + 1
            model = BudgetModel(
                id=new_id,
                name=name,
                start=start_dt,
                end=end_dt,
                amount=amount,
            )
            self._controller.budgets_manager.create_budget(model)
        else:
            model = BudgetModel(
                id=self._budget.id,
                name=name,
                start=start_dt,
                end=end_dt,
                amount=amount,
            )
            updated = self._controller.budgets_manager.update_budget(self._budget.id, model)
            if updated is None:
                self.show_error("Failed to update budget (not found).")
                return

        self.accept()

