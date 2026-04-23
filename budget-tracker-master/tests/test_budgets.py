import unittest
from unittest.mock import patch
from app.budget.budget_manager import BudgetManager
from datetime import datetime
from tests.commons import create_test_budget


class TestBudgetManager(unittest.TestCase):
    def setUp(self):
        self._load_patcher = patch.object(
            BudgetManager,
            "load_budgets",
            autospec=True,
        )
        self._save_patcher = patch.object(
            BudgetManager,
            "save_budgets",
            autospec=True,
        )
        self._load_patcher.start()
        self._save_patcher.start()
        self.addCleanup(self._load_patcher.stop)
        self.addCleanup(self._save_patcher.stop)
        self.budget_manager = BudgetManager()

    def test_create_budget(self):
        budget = create_test_budget()
        self.budget_manager.create_budget(budget)
        self.assertEqual(len(self.budget_manager.budgets), 1)
        self.assertEqual(self.budget_manager.budgets[0], budget)

    def test_read_budget(self):
        budget = create_test_budget()
        self.budget_manager.create_budget(budget)
        self.assertEqual(self.budget_manager.read_budget(budget.id), budget)

    def test_update_budget(self):
        budget = create_test_budget()
        self.budget_manager.create_budget(budget)
        budget = create_test_budget(id=1, amount=200.0)
        updated_budget = self.budget_manager.update_budget(1, budget)
        self.assertEqual(self.budget_manager.read_budget(1).amount, 200.0)
        self.assertEqual(updated_budget, budget)

    def test_delete_budget(self):
        budget = create_test_budget()
        self.budget_manager.create_budget(budget)
        self.budget_manager.delete_budget(budget.id)
        self.assertEqual(len(self.budget_manager.budgets), 0)
        self.assertEqual(self.budget_manager.read_budget(budget.id), None)

    def test_get_all_budgets(self):
        budget = create_test_budget()
        self.budget_manager.create_budget(budget)
        self.assertEqual(len(self.budget_manager.get_all_budgets()), 1)

    def test_get_budgets_by_date(self):
        jan_start = datetime(2024, 1, 1)
        jan_end = datetime(2024, 1, 31)
        budget = create_test_budget(start=jan_start, end=jan_end)
        self.budget_manager.create_budget(budget)
        self.assertEqual(len(self.budget_manager.get_budgets_by_date(budget.start)), 1)
        self.assertEqual(self.budget_manager.get_budgets_by_date(budget.start)[0], budget)
        mar_start = datetime(2024, 3, 1)
        mar_end = datetime(2024, 3, 31)
        other = create_test_budget(id=2, start=mar_start, end=mar_end)
        self.budget_manager.create_budget(other)
        self.assertEqual(len(self.budget_manager.get_budgets_by_date(other.end)), 1)