import os
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.agent.api import app as fastapi_app
from app.agent.schemas import BudgetPayload, NotificationRulePayload, TransactionPayload
from app.agent.service import BudgetTrackerService


class TestAgentInterfaces(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.env = patch.dict(
            os.environ,
            {
                "DATA_DIR": self.tmpdir.name,
                "BUDGET_FILE": os.path.join(self.tmpdir.name, "budgets.csv"),
                "TRANSACTION_FILE": os.path.join(self.tmpdir.name, "transactions.csv"),
                "NOTIFICATION_RULE_FILE": os.path.join(
                    self.tmpdir.name, "notification_rules.csv"
                ),
                "NOTIFICATION_FILE": os.path.join(self.tmpdir.name, "notifications.csv"),
            },
            clear=False,
        )
        self.env.start()
        self.addCleanup(self.env.stop)
        self.service = BudgetTrackerService()

    def test_fastapi_app_imports(self):
        self.assertEqual(fastapi_app.title, "BudgetTracker Agent API")

    def test_transaction_budget_rule_crud(self):
        now = datetime.now()
        transaction = self.service.create_transaction(
            TransactionPayload(
                timestamp=int(now.timestamp()),
                category="Food",
                amount=-12.5,
                tag="Lunch",
            )
        )
        budget = self.service.create_budget(
            BudgetPayload(
                name="Food Budget",
                start=now.replace(day=1),
                end=now.replace(day=28) + timedelta(days=4),
                amount=500.0,
            )
        )
        rule = self.service.create_rule(
            NotificationRulePayload(
                name="Over budget",
                rule="WHERE transaction.amount < 0 AND budget.amount > 0",
                message="Budget rule matched",
            )
        )

        self.assertEqual(self.service.get_transaction(transaction.id), transaction)
        self.assertEqual(self.service.get_budget(budget.id), budget)
        self.assertEqual(self.service.get_rule(rule.id), rule)
        self.assertGreaterEqual(self.service.summary()["transaction_count"], 1)
        self.assertGreaterEqual(len(self.service.notifications()), 0)

        self.assertTrue(self.service.delete_transaction(transaction.id))
        self.assertTrue(self.service.delete_budget(budget.id))
        self.assertTrue(self.service.delete_rule(rule.id))

        self.assertIsNone(self.service.get_transaction(transaction.id))
        self.assertIsNone(self.service.get_budget(budget.id))
        self.assertIsNone(self.service.get_rule(rule.id))
