import unittest
from app.statistic.ratings import top_week, top_month, top_year
from app.transaction.transaction_manager import TransactionManager
from app.budget.budget_manager import BudgetManager

class TestStatistic(unittest.TestCase):
    def setUp(self):
        self.transaction_manager = TransactionManager()
        self.budget_manager = BudgetManager()

    def test_top_week(self):
        transaction = create_test_transaction()
        self.transaction_manager.create_transaction(transaction)
        self.assertEqual(top_week(self.transaction_manager.transactions), [transaction])

    def test_top_month(self):
        self.assertEqual(top_month(self.transaction_manager.transactions), [])

    def test_top_year(self):
        self.assertEqual(top_year(self.transaction_manager.transactions), [])