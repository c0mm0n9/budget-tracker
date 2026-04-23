from __future__ import annotations

from typing import Optional

from app.config import Config
from app.storage.budget_model import BudgetModel
from app.storage.csv_handler import read_csv_dicts, write_csv_dicts
from app.storage.notification_rule import NotificationRuleModel
from app.storage.transaction_model import TransactionModel
from app.warnings.rule_expression import (
    ParsedRule,
    RuleSyntaxError,
    evaluate_rule,
    parse_notification_rule,
)

NOTIFICATION_RULE_COLUMNS = ["id", "name", "rule", "message"]


class NotificationRulesManager:
    def __init__(self):
        self.notification_rules: list[NotificationRuleModel] = []
        self.config = Config()
        self.load_notification_rules()

    def load_notification_rules(self) -> None:
        self.notification_rules = []
        for row in read_csv_dicts(self.config.NOTIFICATION_RULE_FILE):
            try:
                raw_id = (row.get("id") or "").strip()
                if not raw_id:
                    continue
                self.notification_rules.append(
                    NotificationRuleModel(
                        id=int(raw_id),
                        name=str(row.get("name") or "").strip(),
                        rule=str(row.get("rule") or "").strip(),
                        message=str(row.get("message") or "").strip(),
                    )
                )
            except (ValueError, TypeError) as e:
                print(f"Error loading notification rule: {e}")
                continue

    def save_notification_rules(self) -> None:
        rows = [r.model_dump() for r in self.notification_rules]
        write_csv_dicts(self.config.NOTIFICATION_RULE_FILE, rows, NOTIFICATION_RULE_COLUMNS)

    def create_notification_rule(
        self, notification_rule: NotificationRuleModel
    ) -> NotificationRuleModel:
        self.notification_rules.append(notification_rule)
        self.save_notification_rules()
        return notification_rule

    def read_notification_rule(self, id: int) -> Optional[NotificationRuleModel]:
        return next(
            (
                notification_rule
                for notification_rule in self.notification_rules
                if notification_rule.id == id
            ),
            None,
        )

    def update_notification_rule(
        self, id: int, notification_rule: NotificationRuleModel
    ) -> Optional[NotificationRuleModel]:
        for i, n in enumerate(self.notification_rules):
            if n.id == id:
                self.notification_rules[i] = notification_rule
                self.save_notification_rules()
                return self.notification_rules[i]
        return None

    def delete_notification_rule(self, id: int) -> bool:
        for i, n in enumerate(self.notification_rules):
            if n.id == id:
                self.notification_rules.pop(i)
                self.save_notification_rules()
                return True
        return False

    def get_all_notification_rules(self) -> list[NotificationRuleModel]:
        return self.notification_rules

    def check_notifications(
        self,
        transactions: list[TransactionModel],
        budgets: list[BudgetModel],
    ) -> Optional[str]:
        matches = self.check_all_notifications(transactions, budgets)
        if not matches:
            return None
        return matches[0]

    def check_all_notifications(
        self,
        transactions: list[TransactionModel],
        budgets: list[BudgetModel],
    ) -> list[str]:
        if not transactions or not budgets:
            return []

        matches: list[str] = []
        for notification_rule in self.notification_rules:
            try:
                parsed = parse_notification_rule(notification_rule.rule)
            except RuleSyntaxError:
                continue

            matched = False
            for t in transactions:
                for b in budgets:
                    if evaluate_rule(parsed, t, b):
                        matches.append(notification_rule.message or notification_rule.name)
                        # A rule should be listed once, even if many tx/budget pairs match.
                        matched = True
                        break
                if matched:
                    break
        return matches

    @staticmethod
    def parse_rule_text(rule: str) -> ParsedRule:
        """Validate and parse rule text into an internal AST (for tests / tooling)."""
        return parse_notification_rule(rule)

    def check_notification(
        self,
        rule: str | NotificationRuleModel,
        transaction: TransactionModel,
        budget: BudgetModel,
    ) -> bool:
        text = rule.rule if isinstance(rule, NotificationRuleModel) else rule
        parsed = parse_notification_rule(text)
        return evaluate_rule(parsed, transaction, budget)
