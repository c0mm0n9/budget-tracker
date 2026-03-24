from app.storage.transaction_model import TransactionModel
from app.storage.budget_model import BudgetModel
from datetime import datetime, timedelta

def create_test_transaction(
    id: int = 1, 
    timestamp: int = 1716153600, 
    category: str = "Test", 
    amount: float = 100.0, 
    tag: str = "Test"
    ) -> TransactionModel:
    """
    Create a test transaction.
    """
    return TransactionModel(id=id, timestamp=timestamp, category=category, amount=amount, tag=tag)

def create_test_budget(
    id: int = 1,
    name: str = "Test",
    start: datetime = datetime.now(),
    end: datetime = datetime.now() + timedelta(days=30),
    amount: float = 100.0
) -> BudgetModel:
    """
    Create a test budget.
    """
    return BudgetModel(id=id, name=name, start=start, end=end, amount=amount)