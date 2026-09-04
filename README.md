
# Personal finance management

## *Updates* 🔥

- **[2026/09]** Semantic tool routing — the agent embeds your question and picks only the most relevant sheet tools before calling the LLM
- **[2026/09]** Google-Sheet transaction tools for retrieving and counting records across single, multiple and all worksheets
- **[2026/08]** LangGraph agent graph with tool-error retry loop and token tracking

## Quick Start

```bash
# 1. Clone and set up the environment
git clone <your-repo-url> personal-finance-manager
cd personal-finance-manager

# Create the conda environment and install dependencies
conda create -n pfm python=3.11 -y
conda activate pfm
pip install -r requirements.txt   # or: conda env update -f environment.yml

# 2. Configure your local environment
cp .env.example .env
# Edit .env with your LLM, embedding and Google Sheet credentials

# 3. Run the agent
python main.py
```

## Installation

### Google Sheet Access

The tools read a Google Sheet via `gspread` using a service-account JSON:

```bash
# Point CREDENTIAL at your service-account file and SHEET_KEY at the sheet
CREDENTIAL=path/to/service_account.json
SHEET_KEY=your_spreadsheet_key
```

## Configuration

All settings are loaded from environment variables (via `.env`, managed with `pydantic-settings`). Copy the example and adjust:

```bash
cp .env.example .env
```

### Agent

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM backend | `ollama` |
| `LLM_MODEL` | Chat model name | `gemma4:26b` |
| `LLM_REASONING` | Enable reasoning mode | `true` |
| `MAX_TOOL_RETRY` | Max retries on tool failure | `5` |

### Semantic Router

| Variable | Description | Example |
|----------|-------------|---------|
| `ROUTER_TYPE` | Router strategy | `semantic` |
| `ROUTER_PROVIDER` | Embedding backend for routing | `ollama` |
| `ROUTER_MODEL` | Embedding model for routing | `gemma4:26b` |
| `TOOL_KB` | Path to the tool knowledge base JSON | `data/tool_kb.json` |

### Embedding

| Variable | Description | Example |
|----------|-------------|---------|
| `EMBEDDING_PROVIDER` | Embedding backend | `ollama` |
| `EMBEDDING_MODEL` | Embedding model | `nomic-embed-text-v2-moe:latest` |
| `DIMENSION` | Embedding dimension (blank = auto) | `768` |

### Google Sheet

| Variable | Description | Example |
|----------|-------------|---------|
| `CREDENTIAL` | Path to service-account JSON | `path/to/service_account.json` |
| `SHEET_KEY` | Spreadsheet key | `<key>` |

### Logging

| Variable | Description | Example |
|----------|-------------|---------|
| `LOG_FILE` | Log output file | `logs/app.log` |
| `LOG_LEVEL` | Log verbosity | `INFO` |

## Architecture

### System Overview

The agent is a compiled LangGraph `StateGraph`. A user prompt enters the **router**, which semantically selects the most relevant sheet tools; the LLM is then bound to exactly those tools, executes them, and a check node either retries on failure or hands the result back to the LLM for a natural-language answer.

```
┌──────────────────────────────────────────────────────────┐
│                    User Input (Vietnamese)               │
│                      (Entry Point)                       │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│  ROUTER (Semantic Tool Router)                           │
│  • Embeds the user question                              │
│  • Cosine-matches against the tool knowledge base        │
│  • Returns the top-k tools above a threshold             │
└──────────────────────────┬───────────────────────────────┘
                           │
                 ┌─────────┴─────────┐
        (no tools)│          │(tools matched)
                  ▼          ▼
          ┌──────────┐  ┌────────────────────────────────┐
          │   LLM    │  │  LLM-BIND-TOOL                 │
          │ (answer) │  │  • Binds only matched tools    │
          └────┬─────┘  │  • Emits tool_calls            │
               │         └──────────────┬─────────────────┘
               │                        ▼
               │         ┌────────────────────────────────┐
               │         │  TOOLS (ToolNode)              │
               │         │  • get / count / all, single & │
               │         │    multi-sheet (Google Sheet)  │
               │         └──────────────┬─────────────────┘
               │                        ▼
               │         ┌────────────────────────────────┐
               │         │  CHECK-TOOL-ERROR              │
               │         │  • error + retries left → bind  │
               │         │  • success / max retries → llm  │
               │         └──────────────┬─────────────────┘
               │                        │
               ▼                        ▼
          ┌────────────────────────────────────────────────┐
          │                   END                           │
          │        Final Vietnamese answer                  │
          └────────────────────────────────────────────────┘
```

## Tools

The agent exposes Google-Sheet transaction tools under `src/tools/gg_sheet`, covering retrieval and counting:

| Tool | Scope | Purpose |
|------|-------|---------|
| `get_transaction` | Single sheet | Read rows from one worksheet with filters |
| `get_transaction_multi_sheet` | Multiple sheets | Read rows from several worksheets at once |
| `get_all_transactions` | All sheets | Read rows from every worksheet |
| `count_transaction` | Single sheet | Count matching rows in one worksheet |
| `count_transaction_multi_sheet` | Multiple sheets | Count matching rows across worksheets |
| `count_all_transactions` | All sheets | Count matching rows across all worksheets |

Filters available across tools: `from_date`, `to_date`, `from_amount`, `to_amount`, `transaction_type` (`Nhận` / `Chi`), `description`, and `payment_method` (`Thẻ` / `Tiền mặt`).

## Usage

```python
from src.agent import LangGraphAgent

agent = LangGraphAgent()

history = [
    "Đếm số giao dịch của Tháng 2"
]

result = agent.invoke_graph(history)
print(result["messages"][-1].content)
```

The same entry point is used by `main.py`, which boots the agent and runs a sample prompt.
