# BudgetTrackeer

A desktop budget tracking app built with Python and PyQt6.

## Requirements

- Python 3.10+ (3.11 recommended)
- `pip`

## Setup

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the app

From the project root:

```powershell
python -m app.ui
```

## Agent-friendly entry points

### CLI

```powershell
python -m app.agent transactions list
python -m app.agent stats summary
```

### HTTP API

```powershell
uvicorn app.agent.api:app --reload
```

### MCP server

```powershell
python -m app.agent.mcp_server
```

## Run tests

From the project root:

```powershell
python -m unittest discover -s tests
```

## Data/config notes

- By default, data files are created in the `data/` folder.
- You can override file paths with environment variables in a `.env` file:
  - `DATA_DIR`
  - `BUDGET_FILE`
  - `TRANSACTION_FILE`
  - `NOTIFICATION_RULE_FILE`
  - `NOTIFICATION_FILE`

## Architecture

```mermaid 
 graph TD
    subgraph UI["UI Layer"]
        CLI["CLI Menu<br/>User commands"]
    end

    subgraph Core["Core Logic"]
        
        subgraph Stats["Statistics Module"]
            subgraph Rating["Ratings"]
                TopWeek["Top Week<br/>Highest spending"]
                TopMonth["Top Month<br/>Highest spending"]
            end

            subgraph Groupers["Groupers"]
                ByCat["By Category<br/>Group spending"]
                ByTag["By Tag<br/>Group spending"]
            end

            subgraph Other["Other"]
                MinMax["Min/Max<br/>Biggest & Smallest"]
                AvgMonth["Average<br/>This Month"]
                AvgWeek["Average<br/>This Week"]
            end
        end

        subgraph Transaction["Transaction Module"]
            CRUD_T["CRUD Operations"]
        end

        subgraph Budget["Budget Manager"]
            CRUD_B["CRUD Operations"]

        end

        subgraph Warnings["Warnings Module"]
            CRUD_N["CRUD Operations"]
        end
    end

    subgraph Storage["Storage Layer"]
        subgraph Models["Pydantic Models"]
            TransModel["Transaction Model<br/>ID:int\nTimestamp:int\nCategory:str\nAmount:float\nTag:str"]
            BudgetModel["Budget Model<br/>ID:int\nName:str\nStart:DateTime\nEnd:DateTime\nAmount:float"]
            NotificationRuleModel["Notification Rule Model<br/>ID:int\nName:str\nRule:str (SQL Query-like string)"]
        end

        CSVHandler["CSV Handler\nCRUD Operations"]

        subgraph Files["CSV Files"]
            TransCSV["transactions.csv"]
            BudgetCSV["budgets.csv"]
            RulesCSV["rules.csv"]
        end
    end

    UI --- Handlers

    Handlers --- Stats
    Handlers --- Budget
    Handlers --- Warnings
    Handlers --- Transaction

    CRUD_T --- TransModel
    CRUD_B --- BudgetModel
    CRUD_N --- NotificationRuleModel

    TransModel --- CSVHandler
    BudgetModel --- CSVHandler
    NotificationRuleModel --- CSVHandler

    CSVHandler --- Files

    style UI fill:#85B7EB,stroke:#185FA5,color:#042C53,stroke-width:2px
    style Core fill:#E1F5EE,stroke:#0F6E56,color:#085041,stroke-width:2px
    style Transaction fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:1.5px
    style Stats fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:1.5px
    style Budget fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:1.5px
    style Warnings fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:1.5px
    style Storage fill:#FAEEDA,stroke:#854F0B,color:#412402,stroke-width:2px
    style Models fill:#EF9F27,stroke:#854F0B,color:#412402,stroke-width:1.5px
    style Handlers fill:#EF9F27,stroke:#854F0B,color:#412402,stroke-width:1.5px
    style Files fill:#BA7517,stroke:#854F0B,color:#fff,stroke-width:1.5px

    style UI fill:#85B7EB,stroke:#185FA5,color:#042C53,stroke-width:3px
    style CLI fill:#B5D4F4,stroke:#0C447C,color:#042C53,stroke-width:2px

    style Core fill:#E1F5EE,stroke:#0F6E56,color:#085041,stroke-width:3px
    style Stats fill:#9FE1CB,stroke:#0F6E56,color:#085041,stroke-width:2px
    style Rating fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:1.5px
    style Groupers fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:1.5px
    style Other fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:1.5px
    
    style TopWeek fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style TopMonth fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style ByCat fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style ByTag fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style MinMax fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style AvgMonth fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style AvgWeek fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
 
    style Transaction fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:2px
    style Budget fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:2px
    style Warnings fill:#5DCAA5,stroke:#0F6E56,color:#04342C,stroke-width:2px
 
    style CRUD_T fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style CRUD_B fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
    style CRUD_N fill:#E1F5EE,stroke:#085041,color:#04342C,stroke-width:1px
 
    style Storage fill:#FAEEDA,stroke:#854F0B,color:#412402,stroke-width:3px
    style Models fill:#EF9F27,stroke:#854F0B,color:#412402,stroke-width:2px
    style TransModel fill:#FAC775,stroke:#BA7517,color:#412402,stroke-width:1px
    style BudgetModel fill:#FAC775,stroke:#BA7517,color:#412402,stroke-width:1px
    style NotificationRuleModel fill:#FAC775,stroke:#BA7517,color:#412402,stroke-width:1px
 
    style CSVHandler fill:#EF9F27,stroke:#854F0B,color:#412402,stroke-width:2px
 
    style Files fill:#BA7517,stroke:#854F0B,color:#fff,stroke-width:2px
    style TransCSV fill:#854F0B,stroke:#633806,color:#fff,stroke-width:1px
    style BudgetCSV fill:#854F0B,stroke:#633806,color:#fff,stroke-width:1px
    style RulesCSV fill:#854F0B,stroke:#633806,color:#fff,stroke-width:1px
 
    linkStyle default stroke:#5F5E5A,stroke-width:2px
```
