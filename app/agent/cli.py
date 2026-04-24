from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .schemas import BudgetPayload, NotificationRulePayload, TransactionPayload
from .service import BudgetTrackerService


def _dump(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def _load_payload(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON payload: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Payload must be a JSON object")
    return data


def _add_resource_parser(subparsers: argparse._SubParsersAction, name: str):
    return subparsers.add_parser(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="budget-tracker", description="BudgetTracker CLI")
    subparsers = parser.add_subparsers(dest="resource", required=True)

    tx = _add_resource_parser(subparsers, "transactions")
    tx_sub = tx.add_subparsers(dest="action", required=True)
    tx_sub.add_parser("list")
    tx_get = tx_sub.add_parser("get")
    tx_get.add_argument("id", type=int)
    tx_create = tx_sub.add_parser("create")
    tx_create.add_argument("--payload", required=True)
    tx_update = tx_sub.add_parser("update")
    tx_update.add_argument("id", type=int)
    tx_update.add_argument("--payload", required=True)
    tx_delete = tx_sub.add_parser("delete")
    tx_delete.add_argument("id", type=int)

    budgets = _add_resource_parser(subparsers, "budgets")
    budget_sub = budgets.add_subparsers(dest="action", required=True)
    budget_sub.add_parser("list")
    budget_get = budget_sub.add_parser("get")
    budget_get.add_argument("id", type=int)
    budget_create = budget_sub.add_parser("create")
    budget_create.add_argument("--payload", required=True)
    budget_update = budget_sub.add_parser("update")
    budget_update.add_argument("id", type=int)
    budget_update.add_argument("--payload", required=True)
    budget_delete = budget_sub.add_parser("delete")
    budget_delete.add_argument("id", type=int)

    rules = _add_resource_parser(subparsers, "rules")
    rule_sub = rules.add_subparsers(dest="action", required=True)
    rule_sub.add_parser("list")
    rule_get = rule_sub.add_parser("get")
    rule_get.add_argument("id", type=int)
    rule_create = rule_sub.add_parser("create")
    rule_create.add_argument("--payload", required=True)
    rule_update = rule_sub.add_parser("update")
    rule_update.add_argument("id", type=int)
    rule_update.add_argument("--payload", required=True)
    rule_delete = rule_sub.add_parser("delete")
    rule_delete.add_argument("id", type=int)

    stats = _add_resource_parser(subparsers, "stats")
    stats_sub = stats.add_subparsers(dest="action", required=True)
    stats_sub.add_parser("summary")
    stats_sub.add_parser("notifications")
    stats_sub.add_parser("monthly-totals")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = BudgetTrackerService()

    try:
        if args.resource == "transactions":
            if args.action == "list":
                _dump([item.model_dump(mode="json") for item in service.list_transactions()])
            elif args.action == "get":
                item = service.get_transaction(args.id)
                if item is None:
                    raise KeyError(f"Transaction {args.id} not found")
                _dump(item.model_dump(mode="json"))
            elif args.action == "create":
                _dump(service.create_transaction(TransactionPayload.model_validate(_load_payload(args.payload))).model_dump(mode="json"))
            elif args.action == "update":
                _dump(service.update_transaction(args.id, TransactionPayload.model_validate(_load_payload(args.payload))).model_dump(mode="json"))
            elif args.action == "delete":
                _dump({"deleted": service.delete_transaction(args.id)})
        elif args.resource == "budgets":
            if args.action == "list":
                _dump([item.model_dump(mode="json") for item in service.list_budgets()])
            elif args.action == "get":
                item = service.get_budget(args.id)
                if item is None:
                    raise KeyError(f"Budget {args.id} not found")
                _dump(item.model_dump(mode="json"))
            elif args.action == "create":
                _dump(service.create_budget(BudgetPayload.model_validate(_load_payload(args.payload))).model_dump(mode="json"))
            elif args.action == "update":
                _dump(service.update_budget(args.id, BudgetPayload.model_validate(_load_payload(args.payload))).model_dump(mode="json"))
            elif args.action == "delete":
                _dump({"deleted": service.delete_budget(args.id)})
        elif args.resource == "rules":
            if args.action == "list":
                _dump([item.model_dump(mode="json") for item in service.list_rules()])
            elif args.action == "get":
                item = service.get_rule(args.id)
                if item is None:
                    raise KeyError(f"Rule {args.id} not found")
                _dump(item.model_dump(mode="json"))
            elif args.action == "create":
                _dump(service.create_rule(NotificationRulePayload.model_validate(_load_payload(args.payload))).model_dump(mode="json"))
            elif args.action == "update":
                _dump(service.update_rule(args.id, NotificationRulePayload.model_validate(_load_payload(args.payload))).model_dump(mode="json"))
            elif args.action == "delete":
                _dump({"deleted": service.delete_rule(args.id)})
        elif args.resource == "stats":
            if args.action == "summary":
                _dump(service.summary())
            elif args.action == "notifications":
                _dump(service.notifications())
            elif args.action == "monthly-totals":
                _dump(service.summary()["monthly_totals"])
        return 0
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
