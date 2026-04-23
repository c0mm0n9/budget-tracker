# BudgetTracker MCP Integration

This project exposes a Model Context Protocol (MCP) server so AI agents and users can connect to the budget tracker in a standard way.

## What this gives you

- Read-only context through MCP resources
- Action tools for transactions, budgets, and notification rules
- Summary and notification helpers for quick dashboard-style access
- A shared service layer used by CLI, HTTP API, MCP, and the GUI

## How to run the MCP server

From the project root:

```powershell
python -m app.agent.mcp_server
```

By default, this runs over `stdio`, which is the easiest mode for local AI tools and desktop agents.

You can also choose another transport:

```powershell
python -m app.agent.mcp_server --transport streamable-http
python -m app.agent.mcp_server --transport sse
```

## Available MCP resources

Resources are for reading state without changing it.

- `budgettracker://summary`
- `budgettracker://transactions`
- `budgettracker://budgets`
- `budgettracker://rules`

## Available MCP tools

Tools are for actions and lookups.

- `list_transactions`
- `get_transaction`
- `create_transaction`
- `update_transaction`
- `delete_transaction`
- `list_budgets`
- `get_budget`
- `create_budget`
- `update_budget`
- `delete_budget`
- `list_rules`
- `get_rule`
- `create_rule`
- `update_rule`
- `delete_rule`
- `get_summary`
- `get_notifications`

## For AI agents

If you are an agent integrating with this project:

1. Connect to the MCP server using `stdio` first.
2. Read `budgettracker://summary` to understand the current state.
3. Use the list resources when you need full context.
4. Use tools only when you need to mutate data or fetch one object by id.
5. Treat `get_summary` and `get_notifications` as the quickest dashboard-level entry points.

Recommended interaction pattern:

```text
connect -> list tools/resources -> read summary -> perform targeted tool calls -> verify result
```

## For humans

If you just want to use the project locally:

- GUI: `python -m app.ui`
- CLI: `python -m app.agent ...`
- API: `uvicorn app.agent.api:app --reload`
- MCP: `python -m app.agent.mcp_server`

## Data model

- Transaction: `id`, `timestamp`, `category`, `amount`, `tag`
- Budget: `id`, `name`, `start`, `end`, `amount`
- Notification rule: `id`, `name`, `rule`, `message`

## Notes

- Data is stored in CSV files under `data/` by default.
- You can override file locations with environment variables in `.env`.
- The MCP server shares the same underlying storage and business logic as the GUI, CLI, and API.
