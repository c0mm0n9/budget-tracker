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

## Example client configuration

For a local stdio-based MCP client, point it at the project root and use:

```json
{
  "mcpServers": {
    "budget-tracker": {
      "command": "C:\\Users\\huang\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe",
      "args": ["-m", "app.agent.mcp_server"],
      "cwd": "C:\\Users\\huang\\OneDrive\\HKU\\Year 1 Sem 2\\COMP1110\\Group Project\\Codex on COMP1110"
    }
  }
}
```

If your client expects a streamable HTTP endpoint, run:

```powershell
python -m app.agent.mcp_server --transport streamable-http
```

Then connect the client to the corresponding local URL exposed by the server.

## Available MCP resources

Resources are for reading state without changing it.

- `budgettracker://summary`
- `budgettracker://transactions`
- `budgettracker://budgets`
- `budgettracker://rules`
- `budgettracker://transactions/{transaction_id}`
- `budgettracker://budgets/{budget_id}`
- `budgettracker://rules/{rule_id}`

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

## Suggested agent workflow

When an agent first connects, it should:

1. Read `budgettracker://summary`.
2. Open the resource that matches the user request.
3. Use `get_*` tools for one record.
4. Use `list_*` tools for full collections.
5. Use `create_*`, `update_*`, and `delete_*` only after confirming the exact change.

Useful prompts:

- `onboarding_prompt`
- `investigation_prompt`
- `mutation_prompt`

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
- The MCP server also exposes resource templates for one-item reads, which makes agent follow-up requests cleaner and cheaper.
