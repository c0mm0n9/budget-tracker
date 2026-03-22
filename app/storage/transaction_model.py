from pydantic import BaseModel

class TransactionModel(BaseModel):
    id: int
    timestamp: int
    category: str
    amount: float
    tag: str
    