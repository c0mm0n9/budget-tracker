from app.storage.budget_model import BudgetModel
from app.config import Config
from app.storage.csv_handler import read_csv_dicts, write_csv_dicts
from datetime import datetime

class BudgetManager:

    def __init__(self):
        self.budgets: list[BudgetModel] = []
        self.config = Config()
        self.load_budgets()

    def load_budgets(self) -> None:
        self.budgets = []
        for row in read_csv_dicts(self.config.BUDGET_FILE):
            try:
                self.budgets.append(BudgetModel(**row))
            except Exception as e:
                print(f"Error loading budget: {e}")
                continue

    def save_budgets(self) -> None:
        write_csv_dicts(
            self.config.BUDGET_FILE,
            [budget.model_dump() for budget in self.budgets],
            list(BudgetModel.model_fields.keys()),
        )

    def create_budget(self, budget: BudgetModel) -> BudgetModel:
        self.budgets.append(budget)
        self.save_budgets()
        return budget

    def read_budget(self, id: int):
        return next(
            (budget for budget in self.budgets 
            if budget.id == id), None)
            
    def update_budget(self, id: int, budget: BudgetModel) -> BudgetModel:
        for i, b in enumerate(self.budgets):
            if b.id == id:
                self.budgets[i] = budget
                self.save_budgets()
                return self.budgets[i]
        return None
    
    def delete_budget(self, id: int) -> bool:
        for i, b in enumerate(self.budgets):
            if b.id == id:
                self.budgets.pop(i)
                self.save_budgets()
                return True

    def get_all_budgets(self) -> list[BudgetModel]:
        return self.budgets
    
    def get_budgets_by_date(self, date: datetime) -> list[BudgetModel]:
        d = date.date()
        return [
            budget
            for budget in self.budgets
            if budget.start.date() <= d <= budget.end.date()
        ]

    def get_budgets_by_name(self, name: str) -> list[BudgetModel]:
        return [
            budget for budget in self.budgets 
            if budget.name == name
        ]

    def get_budgets_by_amount(self, amount: float) -> list[BudgetModel]:
        return [
            budget for budget in self.budgets 
            if budget.amount == amount
        ]

    def get_budgets_by_start(self, start: datetime) -> list[BudgetModel]:
        d = start.date()
        return [
            budget for budget in self.budgets if budget.start.date() == d
        ]

    def get_budgets_by_end(self, end: datetime) -> list[BudgetModel]:
        d = end.date()
        return [
            budget for budget in self.budgets if budget.end.date() == d
        ]