from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.ui.controllers.app_controller import AppController
from app.storage.budget_model import BudgetModel
from app.storage.notification_rule import NotificationRuleModel
from app.storage.transaction_model import TransactionModel

from .schemas import BudgetPayload, NotificationRulePayload, TransactionPayload


def _jsonable_model(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    raise TypeError(f"Unsupported model type: {type(model)!r}")


@dataclass
class BudgetTrackerService:
    controller: AppController

    def __init__(self) -> None:
        self.controller = AppController()

    def refresh(self) -> None:
        self.controller.refresh()

    @staticmethod
    def _next_id(items: list[Any]) -> int:
        current_ids = [int(getattr(item, "id", 0)) for item in items]
        return max(current_ids, default=0) + 1

    @staticmethod
    def _coerce_transaction(payload: TransactionPayload | dict[str, Any], next_id: int) -> TransactionModel:
        data = payload.model_dump() if isinstance(payload, TransactionPayload) else dict(payload)
        if data.get("id") is None:
            data["id"] = next_id
        return TransactionModel.model_validate(data)

    @staticmethod
    def _coerce_budget(payload: BudgetPayload | dict[str, Any], next_id: int) -> BudgetModel:
        data = payload.model_dump() if isinstance(payload, BudgetPayload) else dict(payload)
        if data.get("id") is None:
            data["id"] = next_id
        return BudgetModel.model_validate(data)

    @staticmethod
    def _coerce_rule(
        payload: NotificationRulePayload | dict[str, Any], next_id: int
    ) -> NotificationRuleModel:
        data = (
            payload.model_dump()
            if isinstance(payload, NotificationRulePayload)
            else dict(payload)
        )
        if data.get("id") is None:
            data["id"] = next_id
        return NotificationRuleModel.model_validate(data)

    def list_transactions(self) -> list[TransactionModel]:
        self.refresh()
        return self.controller.get_transactions()

    def get_transaction(self, id: int) -> TransactionModel | None:
        self.refresh()
        return self.controller.transactions_manager.read_transaction(id)

    def create_transaction(
        self, payload: TransactionPayload | dict[str, Any]
    ) -> TransactionModel:
        self.refresh()
        tx = self._coerce_transaction(
            payload,
            self._next_id(self.controller.transactions_manager.get_all_transactions()),
        )
        if self.controller.transactions_manager.read_transaction(tx.id) is not None:
            raise ValueError(f"Transaction {tx.id} already exists")
        return self.controller.transactions_manager.create_transaction(tx)

    def update_transaction(
        self, id: int, payload: TransactionPayload | dict[str, Any]
    ) -> TransactionModel:
        self.refresh()
        tx = self._coerce_transaction(payload, id)
        updated = self.controller.transactions_manager.update_transaction(id, tx)
        if updated is None:
            raise KeyError(f"Transaction {id} not found")
        return updated

    def delete_transaction(self, id: int) -> bool:
        self.refresh()
        return self.controller.transactions_manager.delete_transaction(id)

    def list_budgets(self) -> list[BudgetModel]:
        self.refresh()
        return self.controller.get_budgets()

    def get_budget(self, id: int) -> BudgetModel | None:
        self.refresh()
        return self.controller.budgets_manager.read_budget(id)

    def create_budget(self, payload: BudgetPayload | dict[str, Any]) -> BudgetModel:
        self.refresh()
        budget = self._coerce_budget(
            payload,
            self._next_id(self.controller.budgets_manager.get_all_budgets()),
        )
        if self.controller.budgets_manager.read_budget(budget.id) is not None:
            raise ValueError(f"Budget {budget.id} already exists")
        return self.controller.budgets_manager.create_budget(budget)

    def update_budget(self, id: int, payload: BudgetPayload | dict[str, Any]) -> BudgetModel:
        self.refresh()
        budget = self._coerce_budget(payload, id)
        updated = self.controller.budgets_manager.update_budget(id, budget)
        if updated is None:
            raise KeyError(f"Budget {id} not found")
        return updated

    def delete_budget(self, id: int) -> bool:
        self.refresh()
        return self.controller.budgets_manager.delete_budget(id)

    def list_rules(self) -> list[NotificationRuleModel]:
        self.refresh()
        return self.controller.get_rules()

    def get_rule(self, id: int) -> NotificationRuleModel | None:
        self.refresh()
        return self.controller.rules_manager.read_notification_rule(id)

    def create_rule(
        self, payload: NotificationRulePayload | dict[str, Any]
    ) -> NotificationRuleModel:
        self.refresh()
        rule = self._coerce_rule(
            payload,
            self._next_id(self.controller.rules_manager.get_all_notification_rules()),
        )
        if self.controller.rules_manager.read_notification_rule(rule.id) is not None:
            raise ValueError(f"Rule {rule.id} already exists")
        return self.controller.rules_manager.create_notification_rule(rule)

    def update_rule(
        self, id: int, payload: NotificationRulePayload | dict[str, Any]
    ) -> NotificationRuleModel:
        self.refresh()
        rule = self._coerce_rule(payload, id)
        updated = self.controller.rules_manager.update_notification_rule(id, rule)
        if updated is None:
            raise KeyError(f"Rule {id} not found")
        return updated

    def delete_rule(self, id: int) -> bool:
        self.refresh()
        return self.controller.rules_manager.delete_notification_rule(id)

    def notifications(self) -> list[str]:
        self.refresh()
        return self.controller.dashboard_notifications()

    def summary(self, now: datetime | None = None) -> dict[str, Any]:
        self.refresh()
        transactions = self.controller.get_transactions()
        budgets = self.controller.get_budgets()
        rules = self.controller.get_rules()
        return {
            "transaction_count": len(transactions),
            "budget_count": len(budgets),
            "rule_count": len(rules),
            "notifications": self.controller.dashboard_notifications(),
            "monthly_spending": self.controller.total_spending_month(now),
            "monthly_average_transaction": self.controller.avg_transaction_month(now),
            "top_spending_transactions": [
                _jsonable_model(tx)
                for tx in self.controller.top_spending_transactions_month(now=now)
            ],
            "top_income_transactions": [
                _jsonable_model(tx)
                for tx in self.controller.top_income_transactions_month(now=now)
            ],
            "monthly_totals": self.controller.monthly_totals_last_n_months(now=now),
            "budget_usage": self.controller.budget_usage_current(now=now),
        }
