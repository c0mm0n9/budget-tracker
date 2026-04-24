from __future__ import annotations

import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP

from .schemas import BudgetPayload, NotificationRulePayload, TransactionPayload
from .service import BudgetTrackerService

mcp = FastMCP(
    "BudgetTracker",
    instructions=(
        "Access transactions, budgets, rules, and statistics for the BudgetTracker app."
    ),
    json_response=True,
)


def _service() -> BudgetTrackerService:
    return BudgetTrackerService()


def _dump_model(item: Any) -> dict[str, Any]:
    return item.model_dump(mode="json")


@mcp.resource("budgettracker://summary")
def summary_resource() -> dict[str, Any]:
    return _service().summary()


@mcp.resource("budgettracker://transactions")
def transactions_resource() -> list[dict[str, Any]]:
    return [_dump_model(item) for item in _service().list_transactions()]


@mcp.resource("budgettracker://transactions/{transaction_id}")
def transaction_resource(transaction_id: int) -> dict[str, Any]:
    item = _service().get_transaction(transaction_id)
    if item is None:
        raise KeyError(f"Transaction {transaction_id} not found")
    return _dump_model(item)


@mcp.resource("budgettracker://budgets")
def budgets_resource() -> list[dict[str, Any]]:
    return [_dump_model(item) for item in _service().list_budgets()]


@mcp.resource("budgettracker://budgets/{budget_id}")
def budget_resource(budget_id: int) -> dict[str, Any]:
    item = _service().get_budget(budget_id)
    if item is None:
        raise KeyError(f"Budget {budget_id} not found")
    return _dump_model(item)


@mcp.resource("budgettracker://rules")
def rules_resource() -> list[dict[str, Any]]:
    return [_dump_model(item) for item in _service().list_rules()]


@mcp.resource("budgettracker://rules/{rule_id}")
def rule_resource(rule_id: int) -> dict[str, Any]:
    item = _service().get_rule(rule_id)
    if item is None:
        raise KeyError(f"Rule {rule_id} not found")
    return _dump_model(item)


@mcp.prompt()
def onboarding_prompt() -> str:
    return (
        "You are connected to BudgetTracker via MCP. "
        "Start by reading budgettracker://summary, then inspect the relevant "
        "resources before changing anything. Use tools for CRUD operations and "
        "prefer id-based reads when you only need one record."
    )


@mcp.prompt()
def investigation_prompt(topic: str = "overall health") -> str:
    return (
        f"Investigate BudgetTracker {topic}. "
        "Read the summary resource first, then inspect transactions, budgets, "
        "or rules as needed. Report notable balances, recent activity, and any "
        "notification matches."
    )


@mcp.prompt()
def mutation_prompt(action: str = "update") -> str:
    return (
        f"Perform a safe {action} against BudgetTracker. "
        "Confirm the current record first, propose the exact change, then use "
        "the matching tool. Verify the result after the tool call."
    )


@mcp.tool()
def list_transactions() -> list[dict[str, Any]]:
    """Return all transactions."""
    return [_dump_model(item) for item in _service().list_transactions()]


@mcp.tool()
def get_transaction(transaction_id: int) -> dict[str, Any]:
    """Return one transaction by id."""
    item = _service().get_transaction(transaction_id)
    if item is None:
        raise KeyError(f"Transaction {transaction_id} not found")
    return _dump_model(item)


@mcp.tool()
def create_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a transaction from JSON payload."""
    return _dump_model(
        _service().create_transaction(TransactionPayload.model_validate(payload))
    )


@mcp.tool()
def update_transaction(transaction_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update a transaction by id."""
    return _dump_model(
        _service().update_transaction(
            transaction_id,
            TransactionPayload.model_validate(payload),
        )
    )


@mcp.tool()
def delete_transaction(transaction_id: int) -> dict[str, bool]:
    """Delete a transaction by id."""
    return {"deleted": _service().delete_transaction(transaction_id)}


@mcp.tool()
def list_budgets() -> list[dict[str, Any]]:
    """Return all budgets."""
    return [_dump_model(item) for item in _service().list_budgets()]


@mcp.tool()
def get_budget(budget_id: int) -> dict[str, Any]:
    """Return one budget by id."""
    item = _service().get_budget(budget_id)
    if item is None:
        raise KeyError(f"Budget {budget_id} not found")
    return _dump_model(item)


@mcp.tool()
def create_budget(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a budget from JSON payload."""
    return _dump_model(_service().create_budget(BudgetPayload.model_validate(payload)))


@mcp.tool()
def update_budget(budget_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update a budget by id."""
    return _dump_model(
        _service().update_budget(
            budget_id,
            BudgetPayload.model_validate(payload),
        )
    )


@mcp.tool()
def delete_budget(budget_id: int) -> dict[str, bool]:
    """Delete a budget by id."""
    return {"deleted": _service().delete_budget(budget_id)}


@mcp.tool()
def list_rules() -> list[dict[str, Any]]:
    """Return all notification rules."""
    return [_dump_model(item) for item in _service().list_rules()]


@mcp.tool()
def get_rule(rule_id: int) -> dict[str, Any]:
    """Return one rule by id."""
    item = _service().get_rule(rule_id)
    if item is None:
        raise KeyError(f"Rule {rule_id} not found")
    return _dump_model(item)


@mcp.tool()
def create_rule(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a notification rule from JSON payload."""
    return _dump_model(
        _service().create_rule(NotificationRulePayload.model_validate(payload))
    )


@mcp.tool()
def update_rule(rule_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update a notification rule by id."""
    return _dump_model(
        _service().update_rule(
            rule_id,
            NotificationRulePayload.model_validate(payload),
        )
    )


@mcp.tool()
def delete_rule(rule_id: int) -> dict[str, bool]:
    """Delete a notification rule by id."""
    return {"deleted": _service().delete_rule(rule_id)}


@mcp.tool()
def get_summary() -> dict[str, Any]:
    """Return a high-level dashboard summary."""
    return _service().summary()


@mcp.tool()
def get_notifications() -> list[str]:
    """Return active dashboard notifications."""
    return _service().notifications()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="budget-tracker-mcp")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http", "sse"),
        default="stdio",
    )
    parser.add_argument("--mount-path", default=None)
    args = parser.parse_args(argv)
    mcp.run(transport=args.transport, mount_path=args.mount_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
