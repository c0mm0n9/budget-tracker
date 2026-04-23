from __future__ import annotations

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

from app.storage.notification_rule import NotificationRuleModel
from app.ui.controllers.app_controller import AppController
from app.ui.design.components import (
    Card,
    EmptyState,
    PrimaryButton,
    SectionHeader,
    style_message_box,
)
from app.ui.dialogs.rule_dialog import RuleDialog


class RulesPage(QWidget):
    def __init__(self, controller: AppController | None = None) -> None:
        super().__init__()
        self._controller = controller or AppController()

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        root.addWidget(SectionHeader("Rules", subtitle="Notification Rules"))

        header = QWidget(self)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        header.setLayout(header_layout)

        header_layout.addStretch(1)

        self._create_btn = PrimaryButton("Create Rule")
        self._create_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self._create_btn, alignment=Qt.AlignmentFlag.AlignRight)

        root.addWidget(header)

        card = Card(self)
        card_layout = card.content_layout
        card_layout.setContentsMargins(0, 0, 0, 0)

        self._empty_state = EmptyState(
            "No notification rules defined.",
            action_text="Create Rule",
            action_callback=self._open_add_dialog,
        )

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["NAME", "RULE", "MESSAGE", "ACTIONS"])
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
        dialog = RuleDialog(self._controller, parent=self)
        from PyQt6.QtWidgets import QDialog

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.refresh()
            self._refresh_table()

    def _open_edit_dialog(self, rule: NotificationRuleModel) -> None:
        dialog = RuleDialog(self._controller, rule=rule, parent=self)
        from PyQt6.QtWidgets import QDialog

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._controller.refresh()
            self._refresh_table()

    def _confirm_delete(self, rule: NotificationRuleModel) -> bool:
        msg = QMessageBox(self)
        style_message_box(msg)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Delete rule?")
        msg.setText(f"Delete rule '{rule.name}'?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        return msg.exec() == QMessageBox.StandardButton.Yes

    def _delete_rule(self, rule: NotificationRuleModel) -> None:
        if not self._confirm_delete(rule):
            return
        self._controller.rules_manager.delete_notification_rule(rule.id)
        self._controller.refresh()
        self._refresh_table()

    def _refresh_table(self) -> None:
        rules = list(self._controller.rules_manager.get_all_notification_rules())
        rules.sort(key=lambda r: r.id, reverse=True)

        self._table.setRowCount(len(rules))

        if not rules:
            self._table.setVisible(False)
            self._empty_state.setVisible(True)
            return

        self._table.setVisible(True)
        self._empty_state.setVisible(False)

        for row, rule in enumerate(rules):
            name_item = QTableWidgetItem(rule.name)
            rule_item = QTableWidgetItem((rule.rule[:80] + "…") if len(rule.rule) > 80 else rule.rule)
            rule_item.setToolTip(rule.rule)
            msg_item = QTableWidgetItem(rule.message or "")

            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, rule_item)
            self._table.setItem(row, 2, msg_item)

            action_cell = QWidget(self._table)
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)
            action_cell.setLayout(layout)

            edit_btn = QPushButton("Edit", action_cell)
            edit_btn.setProperty("variant", "neutral")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda _checked=False, r=rule: self._open_edit_dialog(r))

            del_btn = QPushButton("Delete", action_cell)
            del_btn.setProperty("variant", "danger")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _checked=False, r=rule: self._delete_rule(r))

            for b in (edit_btn, del_btn):
                b.setFixedHeight(28)
                layout.addWidget(b)
                b.style().unpolish(b)
                b.style().polish(b)

            self._table.setCellWidget(row, 3, action_cell)

