import unittest
from unittest.mock import patch
from datetime import datetime, timedelta

from app.statistic.other import average_this_month, average_this_week
from app.statistic.ratings import top_week, top_month, top_year
from app.transaction.transaction_manager import TransactionManager
from app.budget.budget_manager import BudgetManager
from tests.commons import create_test_transaction

class TestStatistic(unittest.TestCase):
    def setUp(self):
        self._load_patcher = patch.object(
            TransactionManager,
            "load_transactions",
            autospec=True,
        )
        self._save_patcher = patch.object(
            TransactionManager,
            "save_transactions",
            autospec=True,
        )
        self._load_patcher.start()
        self._save_patcher.start()
        self.addCleanup(self._load_patcher.stop)
        self.addCleanup(self._save_patcher.stop)
        self.transaction_manager = TransactionManager()
        self.budget_manager = BudgetManager()
        self.now = datetime.now()

    def test_top_week(self):
        week_start = (self.now - timedelta(days=self.now.weekday())).replace(
            hour=12, minute=0, second=0, microsecond=0
        )
        transactions = [
            create_test_transaction(id=1, timestamp=int((week_start + timedelta(days=1)).timestamp()), amount=100.0),
            create_test_transaction(id=2, timestamp=int((week_start + timedelta(days=2)).timestamp()), amount=200.0),
            create_test_transaction(id=3, timestamp=int((week_start - timedelta(days=1)).timestamp()), amount=999.0),
        ]
        for transaction in transactions:
            self.transaction_manager.create_transaction(transaction)

        result = top_week(self.transaction_manager.transactions, now=self.now)
        self.assertEqual(result, [transactions[1], transactions[0]])

    def test_top_month(self):
        month_start = self.now.replace(day=1, hour=12, minute=0, second=0, microsecond=0)
        transactions = [
            create_test_transaction(id=1, timestamp=int((month_start + timedelta(days=1)).timestamp()), amount=100.0),
            create_test_transaction(id=2, timestamp=int((month_start + timedelta(days=2)).timestamp()), amount=250.0),
            create_test_transaction(id=3, timestamp=int((month_start - timedelta(days=1)).timestamp()), amount=999.0),
        ]
        for transaction in transactions:
            self.transaction_manager.create_transaction(transaction)

        result = top_month(self.transaction_manager.transactions, now=self.now)
        self.assertEqual(result, [transactions[1], transactions[0]])

    def test_top_year(self):
        year_start = self.now.replace(month=1, day=1, hour=12, minute=0, second=0, microsecond=0)
        transactions = [
            create_test_transaction(id=1, timestamp=int((year_start + timedelta(days=1)).timestamp()), amount=100.0),
            create_test_transaction(id=2, timestamp=int((year_start + timedelta(days=2)).timestamp()), amount=250.0),
            create_test_transaction(id=3, timestamp=int((year_start - timedelta(days=1)).timestamp()), amount=999.0),
        ]
        for transaction in transactions:
            self.transaction_manager.create_transaction(transaction)

        result = top_year(self.transaction_manager.transactions, now=self.now)
        self.assertEqual(result, [transactions[1], transactions[0]])

    def test_average_helpers_handle_empty_lists(self):
        self.assertEqual(average_this_month([], now=self.now), 0.0)
        self.assertEqual(average_this_week([], now=self.now), 0.0)
