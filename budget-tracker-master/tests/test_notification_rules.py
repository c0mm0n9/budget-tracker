import unittest
from datetime import datetime
from unittest.mock import patch

from app.storage.notification_rule import NotificationRuleModel
from app.warnings.notification_rules_manager import NotificationRulesManager
from app.warnings.rule_expression import (
    RuleSyntaxError,
    evaluate_rule,
    parse_notification_rule,
)
from tests.commons import create_test_budget, create_test_transaction


class TestRuleExpression(unittest.TestCase):
    def test_parse_where_only(self):
        parsed = parse_notification_rule(
            "WHERE transaction.amount > budget.amount",
        )
        self.assertEqual(len(parsed), 1)

    def test_parse_select_prefix(self):
        parsed = parse_notification_rule(
            "SELECT 1 WHERE transaction.amount > budget.amount",
        )
        self.assertEqual(len(parsed), 1)

    def test_parse_and_chain(self):
        parsed = parse_notification_rule(
            "WHERE transaction.category = 'Food' AND transaction.amount > budget.amount",
        )
        self.assertEqual(len(parsed), 2)

    def test_invalid_missing_where(self):
        with self.assertRaises(RuleSyntaxError):
            parse_notification_rule("transaction.amount > 1")

    def test_evaluate_amount_gt(self):
        parsed = parse_notification_rule(
            "WHERE transaction.amount > budget.amount",
        )
        t = create_test_transaction(amount=200.0)
        b = create_test_budget(amount=100.0)
        self.assertTrue(evaluate_rule(parsed, t, b))

    def test_evaluate_amount_gt_false(self):
        parsed = parse_notification_rule(
            "WHERE transaction.amount > budget.amount",
        )
        t = create_test_transaction(amount=50.0)
        b = create_test_budget(amount=100.0)
        self.assertFalse(evaluate_rule(parsed, t, b))

    def test_timestamp_vs_budget_end(self):
        ts = int(datetime(2024, 6, 15).timestamp())
        parsed = parse_notification_rule(
            "WHERE transaction.timestamp < budget.end",
        )
        t = create_test_transaction(timestamp=ts)
        b = create_test_budget(
            start=datetime(2024, 1, 1),
            end=datetime(2024, 12, 31),
        )
        self.assertTrue(evaluate_rule(parsed, t, b))


class TestNotificationRulesManager(unittest.TestCase):
    def setUp(self):
        self._load_patcher = patch.object(
            NotificationRulesManager,
            "load_notification_rules",
            autospec=True,
            side_effect=lambda self: setattr(self, "notification_rules", []),
        )
        self._save_patcher = patch.object(
            NotificationRulesManager,
            "save_notification_rules",
            autospec=True,
        )
        self._load_patcher.start()
        self._save_patcher.start()
        self.addCleanup(self._load_patcher.stop)
        self.addCleanup(self._save_patcher.stop)
        self.manager = NotificationRulesManager()

    def test_check_notification(self):
        rule = NotificationRuleModel(
            id=1,
            name="over",
            rule="WHERE transaction.amount > budget.amount",
        )
        t = create_test_transaction(amount=150.0)
        b = create_test_budget(amount=100.0)
        self.assertTrue(self.manager.check_notification(rule, t, b))

    def test_check_notifications_returns_message(self):
        self.manager.notification_rules = [
            NotificationRuleModel(
                id=1,
                name="over_budget",
                rule="WHERE transaction.amount > budget.amount",
                message="Spending exceeded budget",
            )
        ]
        t = create_test_transaction(amount=200.0)
        b = create_test_budget(amount=100.0)
        msg = self.manager.check_notifications([t], [b])
        self.assertEqual(msg, "Spending exceeded budget")

    def test_check_notifications_falls_back_to_name(self):
        self.manager.notification_rules = [
            NotificationRuleModel(
                id=1,
                name="over_budget",
                rule="WHERE transaction.amount > budget.amount",
            )
        ]
        t = create_test_transaction(amount=200.0)
        b = create_test_budget(amount=100.0)
        msg = self.manager.check_notifications([t], [b])
        self.assertEqual(msg, "over_budget")

    def test_parse_rule_text(self):
        parsed = NotificationRulesManager.parse_rule_text(
            "SELECT * WHERE transaction.tag = 'Test'",
        )
        self.assertEqual(len(parsed), 1)

    def test_check_all_notifications_returns_all_matches(self):
        self.manager.notification_rules = [
            NotificationRuleModel(
                id=1,
                name="over_budget",
                rule="WHERE transaction.amount > budget.amount",
                message="Spending exceeded budget",
            ),
            NotificationRuleModel(
                id=2,
                name="food_category",
                rule="WHERE transaction.category = 'Food'",
                message="Food expense detected",
            ),
        ]
        t = create_test_transaction(amount=200.0, category="Food")
        b = create_test_budget(amount=100.0)
        msgs = self.manager.check_all_notifications([t], [b])
        self.assertEqual(
            msgs,
            ["Spending exceeded budget", "Food expense detected"],
        )

    def test_check_all_notifications_only_adds_rule_once(self):
        self.manager.notification_rules = [
            NotificationRuleModel(
                id=1,
                name="food_category",
                rule="WHERE transaction.category = 'Food'",
                message="Food expense detected",
            ),
        ]
        txs = [
            create_test_transaction(id=1, amount=50.0, category="Food"),
            create_test_transaction(id=2, amount=20.0, category="Food"),
        ]
        b = create_test_budget(amount=1000.0)
        msgs = self.manager.check_all_notifications(txs, [b])
        self.assertEqual(msgs, ["Food expense detected"])
