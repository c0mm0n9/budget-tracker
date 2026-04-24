from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TransactionPayload(BaseModel):
    id: int | None = None
    timestamp: int
    category: str
    amount: float
    tag: str


class BudgetPayload(BaseModel):
    id: int | None = None
    name: str
    start: datetime
    end: datetime
    amount: float


class NotificationRulePayload(BaseModel):
    id: int | None = None
    name: str
    rule: str
    message: str = ""


class SummaryResponse(BaseModel):
    transaction_count: int
    budget_count: int
    rule_count: int
    notifications: list[str]
    monthly_spending: float
    monthly_average_transaction: float
    top_spending_transactions: list[dict]
    top_income_transactions: list[dict]
    monthly_totals: list[tuple[str, float]]
    budget_usage: list[tuple[str, float, float]]
