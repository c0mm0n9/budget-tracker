---
name: budget-tracker
description: "Interact with BudgetTracker via MCP — manage transactions, budgets, and notification rules. Triggers: 'add transaction', 'check budget', 'view spending summary', 'budget alert', 'list transactions', 'create budget', 'notification rule', 'budget tracker', '开支记录', '预算管理', '财务摘要', '消费统计'"
description_zh: "通过 MCP 操作 BudgetTracker，管理交易记录、预算和提醒规则"
description_en: "BudgetTracker MCP integration for transactions, budgets, and notification rules"
version: 1.0.0
---

# BudgetTracker Skill

BudgetTracker is a Python/PyQt6 desktop budget tracking app. This skill lets AI agents interact with it via MCP (Model Context Protocol) — no GUI needed.

## Connection

The MCP server must be running:

```powershell
python -m app.agent.mcp_server
```

It uses stdio by default (recommended for local AI agents).

## Data Models

### Transaction
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique ID (auto-assigned on create) |
| `timestamp` | int | Unix timestamp (seconds since epoch) |
| `category` | string | Spending category (e.g. "food", "transport", "entertainment") |
| `amount` | float | Amount (positive = expense, negative = income) |
| `tag` | string | Optional tag for grouping |

### Budget
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique ID |
| `name` | string | Budget name |
| `start` | datetime | Start datetime |
| `end` | datetime | End datetime |
| `amount` | float | Budget limit |

### NotificationRule
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique ID |
| `name` | string | Rule name |
| `rule` | string | SQL-like query string |
| `message` | string | Notification message template |

## MCP Resources (Read-only)

- `budgettracker://summary` — dashboard overview (spending, budgets, notifications)
- `budgettracker://transactions` — all transactions
- `budgettracker://budgets` — all budgets
- `budgettracker://rules` — all notification rules
- `budgettracker://transactions/{id}` — one transaction
- `budgettracker://budgets/{id}` — one budget
- `budgettracker://rules/{id}` — one rule

## MCP Tools (Actions)

### Transactions
- `list_transactions()` — returns all transactions
- `get_transaction(transaction_id)` — returns one by ID
- `create_transaction(payload)` — creates a transaction
- `update_transaction(transaction_id, payload)` — updates a transaction
- `delete_transaction(transaction_id)` — deletes a transaction

### Budgets
- `list_budgets()` — returns all budgets
- `get_budget(budget_id)` — returns one by ID
- `create_budget(payload)` — creates a budget
- `update_budget(budget_id, payload)` — updates a budget
- `delete_budget(budget_id)` — deletes a budget

### Notification Rules
- `list_rules()` — returns all rules
- `get_rule(rule_id)` — returns one by ID
- `create_rule(payload)` — creates a rule
- `update_rule(rule_id, payload)` — updates a rule
- `delete_rule(rule_id)` — deletes a rule

### Dashboard
- `get_summary()` — high-level summary (monthly spending, top transactions, budget usage)
- `get_notifications()` — active notification messages

## Agent Workflow

1. **Connect** to the MCP server (stdio)
2. **Read** `budgettracker://summary` to understand current state
3. **Inspect** relevant resources (transactions, budgets, rules)
4. **Use tools** for CRUD operations — always confirm before mutation
5. **Verify** result after create/update/delete

## Example Interactions

### Add a transaction
```
create_transaction({
  "timestamp": 1745430000,
  "category": "food",
  "amount": 45.5,
  "tag": "lunch"
})
```

### Check monthly spending
```
get_summary()  # returns monthly_spending, top_transactions, budget_usage
```

### Create a budget
```
create_budget({
  "name": "Monthly Food",
  "start": "2026-04-01T00:00:00",
  "end": "2026-04-30T23:59:59",
  "amount": 2000.0
})
```

### List all transactions
```
list_transactions()
```

## All Entry Points

| Interface | Command |
|-----------|---------|
| GUI | `python -m app.ui` |
| CLI | `python -m app.agent transactions list` |
| HTTP API | `uvicorn app.agent.api:app --reload` |
| MCP | `python -m app.agent.mcp_server` |

All four share the same underlying logic and data (CSV files in `data/`).
