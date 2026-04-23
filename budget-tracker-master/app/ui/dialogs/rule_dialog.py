from __future__ import annotations

import re
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.storage.notification_rule import NotificationRuleModel
from app.ui.controllers.app_controller import AppController
from app.ui.design.components import StandardDialog
from app.warnings.rule_expression import (
    FieldRef,
    LiteralValue,
    RuleSyntaxError,
    parse_notification_rule,
)

OPERATORS = ["!=", "<=", ">=", "=", "<", ">"]
FIELD_OPTIONS = [
    "transaction.id",
    "transaction.timestamp",
    "transaction.category",
    "transaction.amount",
    "transaction.tag",
    "budget.id",
    "budget.name",
    "budget.start",
    "budget.end",
    "budget.amount",
]


@dataclass
class ConditionRow:
    container: QWidget
    left_field: QComboBox
    operator: QComboBox
    right_mode: QComboBox
    right_field: QComboBox
    right_value: QLineEdit
    remove_btn: QPushButton


class RuleDialog(StandardDialog):
    def __init__(
        self,
        controller: AppController,
        *,
        rule: NotificationRuleModel | None = None,
        parent: QWidget | None = None,
    ) -> None:
        title = "Edit Rule" if rule else "Create Rule"
        super().__init__(title=title, parent=parent)
        if rule is None:
            self.set_save_text("Create")

        self._controller = controller
        self._rule = rule

        self._name_edit = QLineEdit(self)
        self._name_edit.setPlaceholderText("Rule name")

        self._message_edit = QLineEdit(self)
        self._message_edit.setPlaceholderText("Optional message")

        self.content_layout.addWidget(self._field_label_pair("Name", self._name_edit))

        self._conditions_wrap = QWidget(self)
        self._conditions_layout = QVBoxLayout()
        self._conditions_layout.setContentsMargins(0, 0, 0, 0)
        self._conditions_layout.setSpacing(8)
        self._conditions_wrap.setLayout(self._conditions_layout)
        self._rows: list[ConditionRow] = []

        self.content_layout.addWidget(
            self._field_label_pair("Rule Conditions (AND)", self._conditions_wrap)
        )

        self._add_condition_btn = QPushButton("+ Add Condition")
        self._add_condition_btn.setProperty("variant", "neutral")
        self._add_condition_btn.clicked.connect(self._on_add_condition)
        self.content_layout.addWidget(self._add_condition_btn)

        self.content_layout.addWidget(
            self._field_label_pair("Message", self._message_edit)
        )

        if rule:
            self._name_edit.setText(rule.name)
            self._message_edit.setText(rule.message or "")
            self._prefill_rows_from_rule(rule.rule)
        else:
            self._on_add_condition()

        self._name_edit.textChanged.connect(self._validate_form)
        self._message_edit.textChanged.connect(self._validate_form)

        self.save_button.clicked.connect(self._on_submit)

        self._validate_form()

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

    def _build_row(self) -> ConditionRow:
        row_widget = QWidget(self)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        row_widget.setLayout(row_layout)

        left_combo = QComboBox(row_widget)
        left_combo.addItems(FIELD_OPTIONS)

        op_combo = QComboBox(row_widget)
        op_combo.addItems(OPERATORS)
        op_combo.setFixedWidth(92)
        op_combo.setMinimumContentsLength(2)

        mode_combo = QComboBox(row_widget)
        mode_combo.addItems(["Field", "Value"])
        mode_combo.setFixedWidth(90)

        right_field_combo = QComboBox(row_widget)
        right_field_combo.addItems(FIELD_OPTIONS)

        right_value_edit = QLineEdit(row_widget)
        right_value_edit.setPlaceholderText("Value (number or text)")
        right_value_edit.hide()

        remove_btn = QPushButton("Remove", row_widget)
        remove_btn.setProperty("variant", "danger")
        remove_btn.setFixedHeight(32)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        row_layout.addWidget(left_combo, 2)
        row_layout.addWidget(op_combo)
        row_layout.addWidget(mode_combo)
        row_layout.addWidget(right_field_combo, 2)
        row_layout.addWidget(right_value_edit, 2)
        row_layout.addWidget(remove_btn)

        left_combo.currentIndexChanged.connect(self._validate_form)
        op_combo.currentIndexChanged.connect(self._validate_form)
        mode_combo.currentIndexChanged.connect(self._validate_form)
        right_field_combo.currentIndexChanged.connect(self._validate_form)
        right_value_edit.textChanged.connect(self._validate_form)

        def on_mode_change() -> None:
            is_field = mode_combo.currentText() == "Field"
            right_field_combo.setVisible(is_field)
            right_value_edit.setVisible(not is_field)
            self._validate_form()

        mode_combo.currentIndexChanged.connect(on_mode_change)
        on_mode_change()

        row = ConditionRow(
            container=row_widget,
            left_field=left_combo,
            operator=op_combo,
            right_mode=mode_combo,
            right_field=right_field_combo,
            right_value=right_value_edit,
            remove_btn=remove_btn,
        )
        remove_btn.clicked.connect(lambda: self._remove_row(row))
        return row

    def _on_add_condition(self) -> None:
        row = self._build_row()
        self._rows.append(row)
        self._conditions_layout.addWidget(row.container)
        self._update_remove_buttons()
        self._validate_form()

    def _remove_row(self, row: ConditionRow) -> None:
        if row not in self._rows:
            return
        self._rows.remove(row)
        row.container.deleteLater()
        self._update_remove_buttons()
        self._validate_form()

    def _update_remove_buttons(self) -> None:
        can_remove = len(self._rows) > 1
        for row in self._rows:
            row.remove_btn.setEnabled(can_remove)

    def _quote_literal(self, text: str) -> str:
        escaped = text.replace("'", "''")
        return f"'{escaped}'"

    def _serialize_right_operand(self, row: ConditionRow) -> str:
        if row.right_mode.currentText() == "Field":
            return row.right_field.currentText()

        raw = row.right_value.text().strip()
        if not raw:
            raise RuleSyntaxError("Right value is required")

        if re.fullmatch(r"-?\d+", raw):
            return raw
        if re.fullmatch(r"-?\d+\.\d+", raw):
            return raw
        return self._quote_literal(raw)

    def _build_rule_text(self) -> str:
        if not self._rows:
            raise RuleSyntaxError("At least one condition is required")

        clauses: list[str] = []
        for row in self._rows:
            left = row.left_field.currentText().strip()
            op = row.operator.currentText().strip()
            right = self._serialize_right_operand(row)
            if not left or not op or not right:
                raise RuleSyntaxError("Incomplete condition row")
            clauses.append(f"{left} {op} {right}")
        return "WHERE " + " AND ".join(clauses)

    def _prefill_rows_from_rule(self, rule_text: str) -> None:
        try:
            parsed = parse_notification_rule(rule_text)
        except RuleSyntaxError as e:
            self.show_error(f"Cannot edit this rule in builder: {e}")
            self.save_button.setEnabled(False)
            return

        # Remove default rows
        for row in list(self._rows):
            self._remove_row(row)

        for left, op, right in parsed:
            if not isinstance(left, FieldRef):
                self.show_error("This rule uses unsupported format for visual builder.")
                self.save_button.setEnabled(False)
                return
            row = self._build_row()
            self._rows.append(row)
            self._conditions_layout.addWidget(row.container)

            left_value = f"{left.table}.{left.name}"
            row.left_field.setCurrentText(left_value)
            row.operator.setCurrentText(op)

            if isinstance(right, FieldRef):
                row.right_mode.setCurrentText("Field")
                row.right_field.setCurrentText(f"{right.table}.{right.name}")
            elif isinstance(right, LiteralValue):
                row.right_mode.setCurrentText("Value")
                row.right_value.setText(str(right.value))

        self._update_remove_buttons()

    def _validate_form(self) -> None:
        name = self._name_edit.text().strip()

        if not name:
            self.show_error("Name is required.")
            self.save_button.setEnabled(False)
            return

        if not self._rows:
            self.show_error("At least one condition is required.")
            self.save_button.setEnabled(False)
            return

        try:
            rule_text = self._build_rule_text()
            parse_notification_rule(rule_text)
        except RuleSyntaxError as e:
            self.show_error(f"Invalid rule: {e}")
            self.save_button.setEnabled(False)
            return

        self.clear_error()
        self.save_button.setEnabled(True)

    def _on_submit(self) -> None:
        # Validate one more time at submit.
        self._validate_form()
        if not self.save_button.isEnabled():
            return

        name = self._name_edit.text().strip()
        rule_text = self._build_rule_text()
        message = self._message_edit.text().strip()

        if self._rule is None:
            existing = self._controller.rules_manager.get_all_notification_rules()
            new_id = max((r.id for r in existing), default=0) + 1
            model = NotificationRuleModel(
                id=new_id,
                name=name,
                rule=rule_text,
                message=message,
            )
            self._controller.rules_manager.create_notification_rule(model)
        else:
            model = NotificationRuleModel(
                id=self._rule.id,
                name=name,
                rule=rule_text,
                message=message,
            )
            updated = self._controller.rules_manager.update_notification_rule(
                self._rule.id, model
            )
            if updated is None:
                self.show_error("Failed to update rule (not found).")
                return

        self.accept()

