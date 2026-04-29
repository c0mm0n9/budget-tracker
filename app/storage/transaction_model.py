from pydantic import BaseModel
from typing import Optional

class TransactionModel(BaseModel):
    id: int
    timestamp: int
    category: str
    amount: float
    tag: str

    linked_budget: Optional[str] = None
    