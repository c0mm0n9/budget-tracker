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

from app.storage.budget_model import BudgetModel
from app.ui.controllers.app_controller import AppController
from app.ui.design.components import (
    Card,
    EmptyState,
    PrimaryButton,
    SectionHeader,
    style_message_box,
)
from app.ui.dialogs.budget_dialog import BudgetDialog
from app.ui.utils.formatters import format_currency


class BudgetsPage(QWidget):
    def __init__(self, controller: AppController | None = None) -> None:
        super().__init__()
        self._controller = controller or AppController()

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        root.addWidget(SectionHeader("Budgets"))

        header = QWidget(self)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        header.setLayout(header_layout)

        header_layout.addStretch(1)

        self._new_btn = PrimaryButton("New Budget")
        self._new_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self._new_btn, alignment=Qt.AlignmentFlag.AlignRight)

        root.addWidget(header)

        card = Card(self)
        card_layout = card.content_layout
        card_layout.setContentsMargins(0, 0, 0, 0)

        self._empty_state = EmptyState(
            "No budgets defined yet.",
            action_text="New Budget",
            action_callback=self._open_add_dialog,
        )

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["NAME", "START", "END", "AMOUNT", "ACTIONS"])
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
        dialog = BudgetDialog(self._controller, parent=self)
        from PyQt6.QtWidgets import QDialog

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.refresh()
            self._refresh_table()

    def _open_edit_dialog(self, budget: BudgetModel) -> None:
        dialog = BudgetDialog(self._controller, budget=budget, parent=self)
        from PyQt6.QtWidgets import QDialog

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.refresh()
            self._refresh_table()

    def _confirm_delete(self, budget: BudgetModel) -> bool:
        msg = QMessageBox(self)
        style_message_box(msg)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Delete budget?")
        msg.setText(f"Delete budget '{budget.name}'?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        return msg.exec() == QMessageBox.StandardButton.Yes

    def _delete_budget(self, budget: BudgetModel) -> None:
        if not self._confirm_delete(budget):
            return
        self._controller.budgets_manager.delete_budget(budget.id)
        self._controller.refresh()
        self._refresh_table()

    def _refresh_table(self) -> None:
        budgets = list(self._controller.budgets_manager.get_all_budgets())
        budgets.sort(key=lambda b: b.start, reverse=True)

        self._table.setRowCount(len(budgets))

        if not budgets:
            self._table.setVisible(False)
            self._empty_state.setVisible(True)
            return

        self._table.setVisible(True)
        self._empty_state.setVisible(False)

        for row, budget in enumerate(budgets):
            name_item = QTableWidgetItem(budget.name)
            start_item = QTableWidgetItem(budget.start.strftime("%Y-%m-%d"))
            end_item = QTableWidgetItem(budget.end.strftime("%Y-%m-%d"))
            amount_item = QTableWidgetItem(format_currency(float(budget.amount)))

            amount_item.setData(Qt.ItemDataRole.UserRole, float(budget.amount))

            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, start_item)
            self._table.setItem(row, 2, end_item)
            self._table.setItem(row, 3, amount_item)

            action_cell = QWidget(self._table)
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)
            action_cell.setLayout(layout)

            edit_btn = QPushButton("Edit", action_cell)
            edit_btn.setProperty("variant", "neutral")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda _checked=False, b=budget: self._open_edit_dialog(b))

            del_btn = QPushButton("Delete", action_cell)
            del_btn.setProperty("variant", "danger")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _checked=False, b=budget: self._delete_budget(b))

            for bbtn in (edit_btn, del_btn):
                bbtn.setFixedHeight(28)
                layout.addWidget(bbtn)
                bbtn.style().unpolish(bbtn)
                bbtn.style().polish(bbtn)

            self._table.setCellWidget(row, 4, action_cell)

