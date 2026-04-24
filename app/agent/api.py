from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, status

from .schemas import BudgetPayload, NotificationRulePayload, TransactionPayload
from .service import BudgetTrackerService

app = FastAPI(
    title="BudgetTracker Agent API",
    description="HTTP API for budget, transaction, rule, and stats access.",
    version="1.0.0",
)


def _service() -> BudgetTrackerService:
    return BudgetTrackerService()


def _model_dump(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/transactions")
def list_transactions() -> list[dict[str, Any]]:
    return [_model_dump(item) for item in _service().list_transactions()]


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int) -> dict[str, Any]:
    item = _service().get_transaction(transaction_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return _model_dump(item)


@app.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionPayload) -> dict[str, Any]:
    try:
        return _model_dump(_service().create_transaction(payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, payload: TransactionPayload) -> dict[str, Any]:
    try:
        return _model_dump(_service().update_transaction(transaction_id, payload))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int) -> dict[str, bool]:
    return {"deleted": _service().delete_transaction(transaction_id)}


@app.get("/budgets")
def list_budgets() -> list[dict[str, Any]]:
    return [_model_dump(item) for item in _service().list_budgets()]


@app.get("/budgets/{budget_id}")
def get_budget(budget_id: int) -> dict[str, Any]:
    item = _service().get_budget(budget_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return _model_dump(item)


@app.post("/budgets", status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetPayload) -> dict[str, Any]:
    try:
        return _model_dump(_service().create_budget(payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.put("/budgets/{budget_id}")
def update_budget(budget_id: int, payload: BudgetPayload) -> dict[str, Any]:
    try:
        return _model_dump(_service().update_budget(budget_id, payload))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int) -> dict[str, bool]:
    return {"deleted": _service().delete_budget(budget_id)}


@app.get("/rules")
def list_rules() -> list[dict[str, Any]]:
    return [_model_dump(item) for item in _service().list_rules()]


@app.get("/rules/{rule_id}")
def get_rule(rule_id: int) -> dict[str, Any]:
    item = _service().get_rule(rule_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return _model_dump(item)


@app.post("/rules", status_code=status.HTTP_201_CREATED)
def create_rule(payload: NotificationRulePayload) -> dict[str, Any]:
    try:
        return _model_dump(_service().create_rule(payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.put("/rules/{rule_id}")
def update_rule(rule_id: int, payload: NotificationRulePayload) -> dict[str, Any]:
    try:
        return _model_dump(_service().update_rule(rule_id, payload))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int) -> dict[str, bool]:
    return {"deleted": _service().delete_rule(rule_id)}


@app.get("/stats/summary")
def stats_summary() -> dict[str, Any]:
    return _service().summary()


@app.get("/stats/notifications")
def stats_notifications() -> list[str]:
    return _service().notifications()


@app.get("/stats/monthly-totals")
def stats_monthly_totals() -> list[tuple[str, float]]:
    return _service().summary()["monthly_totals"]
