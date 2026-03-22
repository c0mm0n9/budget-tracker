from pydantic import BaseModel
from datetime import datetime

class BudgetModel(BaseModel):
    id: int
    name: str
    start: datetime
    end: datetime
    amount: float