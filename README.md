# TokenCUNT

![Python Version](https://img.shields.io/badge/python-1.20.1-blue)
![Version](https://img.shields.io/badge/version-1.20.1-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Status](https://img.shields.io/badge/status-In%20Progress-orange)

```
 _______    _                    _____  * 
 |__   __|  | |                  / ____|    
    | | ___ | | _____ _ __      | |        
    | |/ _ \| |/ / _ \ '_ \    | |        
    | | (_) |   <  __/ | | |   | |____    
    |_|\___/|_|\_\___|_| |_|    \_____|
```

> **A smart, token-efficient AI layer for developers.**  
> Stop burning credits. Start knowing exactly what you spend.

---

## Why TokenCUNT?

Most AI tools are careless with your tokens — redundant calls, bloated context, zero visibility. TokenCUNT is the opposite:

- **Efficient by design** — smart batching and context compression minimize wasted calls
- **Fully transparent** — see exactly how many tokens every operation costs, before and after
- **You're in control** — set budgets and limits per session or per task

---

## Installation

```bash
# Install TokenCUNT
pip install tokencunt

# Install with CLI dependencies (recommended)
pip install tokencunt[cli]

# Or install in development mode
pip install -e ".[cli,dev]"
```

### Requirements

- Python 3.10+
- MiniMax API key

---

## Quick Start

### 1. Configure your API key

```bash
# Set environment variable
export MINIMAX_API_KEY="your-api-key"
export MINIMAX_GROUP_ID="your-group-id"

# Or create a config file
mkdir -p ~/.tokencunt
cat > ~/.tokencunt/config.yaml << EOF
api_key: "your-api-key"
group_id: "your-group-id"
model: "abab6.5-chat"
default_budget: 10000
EOF
```

### 2. Run the CLI

```bash
# Show logo and welcome
ts start

# Ask a question with full token tracking
ts ask "explain this function" --file main.py

# Dry run — see the cost before committing
ts ask "refactor this" --file app.py

# Analyze a file and get suggestions
ts analyze --file main.py

# Run multiple tasks from a JSON file
ts batch --file tasks.json

# View a usage report for the current session
ts report

# Session management
ts session new
ts session list
ts session config --budget 5000
```

---

## Commands

| Command | Description |
|---------|-------------|
| `ts start` | Show logo and welcome message |
| `ts ask "<prompt>" --file <file>` | Ask a question with token tracking |
| `ts ask ...` (no flags) | Ask a question directly |
| `ts ask ... --dry-run` | Preview token cost without API call |
| `ts analyze --file <file>` | Analyze a file for improvements |
| `ts analyze --file <file> --focus bugs` | Focus on specific area (bugs, performance, style, security) |
| `ts batch --file <json>` | Run multiple tasks from JSON file |
| `ts report` | Show session usage breakdown |
| `ts report --format json` | JSON output for scripting |
| `ts session new` | Create a new session |
| `ts session list` | List all sessions |
| `ts session config --budget 5000` | Set token budget for session |
| `ts session clear` | Clear session data |
| `ts version` | Show version information |

### Global Options

| Option | Description |
|--------|-------------|
| `-q, --quiet` | Minimal output |
| `-v, --verbose` | Verbose output |
| `--json` | JSON output |
| `--debug` | Debug mode with traceback |
| `-y, --yes` | Skip confirmations |

---

### Example Output

```
$ ts ask "what does this function do?" --file utils.py

  Estimated tokens: 312
  ─────────────────────────────────────
  Response: This function takes a list and...
  ─────────────────────────────────────
  Tokens used:  input: 312  output: 89  total: 401
  Session total: 1,204 / 5,000 tokens used (24%)
```

---

## Architecture

```
┌─────────────────────────────────────┐
│         User Interface              │
│   CLI Tool  │  VSCode Extension     │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│           Core Engine               │
│  - Token counter & tracker          │
│  - Smart batcher                   │
│  - Budget enforcer                 │
│  - Prompt optimizer                │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         MiniMax M2.5 API            │
└─────────────────────────────────────┘
```

The core engine is shared — CLI and VSCode extension are just interfaces on top of it.

---

## Project Structure

```
TokenCUNT/
├── src/tokencunt/
│   ├── __init__.py
│   ├── pyproject.toml
│   ├── config.py                 # Configuration management
│   └── core/
│       ├── __init__.py           # Core exports
│       ├── api_client.py         # MiniMax API calls with retry
│       ├── exceptions.py         # Custom exception classes
│       ├── token_counter.py     # Token counting (tiktoken)
│       ├── budget.py            # Budget enforcement & alerts
│       ├── batcher.py           # Combine small requests
│       ├── optimizer.py         # Compress & strip redundant context
│       └── session.py           # Track usage across sessions
├── cli/
│   ├── __init__.py
│   ├── app.py                   # Typer app entry point
│   ├── logo.py                  # ASCII logo
│   ├── exit_codes.py            # Exit codes
│   ├── formatters.py            # Rich output formatting
│   └── commands/
│       ├── __init__.py
│       ├── ask.py               # Ask command
│       ├── analyze.py           # Analyze command
│       ├── batch.py             # Batch command
│       ├── report.py            # Report command
│       └── session.py           # Session management
├── tests/
├── .planning/                    # GSD planning docs
├── ascii-art.txt               # Logo source
├── pyproject.toml              # Project config
└── README.md
```

---

## Tech Stack

| Tool | Role |
|------|------|
| [Typer](https://typer.tiangolo.com/) | CLI framework |
| [Rich](https://github.com/Textualize/rich) | Terminal output formatting |
| [httpx](https://www.python-httpx.org/) | Async HTTP client |
| [tiktoken](https://github.com/openai/tiktoken) | Token counting |
| [Tenacity](https://tenacity.readthedocs.io/) | Retry logic |
| [Pydantic](https://pydantic.dev/) | Data validation |

---

## Configuration

### Environment Variables

```bash
MINIMAX_API_KEY=your-api-key
MINIMAX_GROUP_ID=your-group-id
```

### Config File

Create `~/.tokencunt/config.yaml`:

```yaml
api_key: "your-api-key"
group_id: "your-group-id"
model: "abab6.5-chat"
default_budget: 10000
```

### Priority Order

1. Environment variables (highest priority)
2. Config file
3. Hardcoded defaults (lowest priority)

---

## Roadmap

| Phase | What | Status |
|-------|------|--------|
| 1 | Core engine (Python) | ✅ Done |
| 2 | CLI Tool | ✅ Done |
| 3 | VSCode Extension | 🔲 Planned |

---

## VSCode Extension *(coming soon)*

The extension will sit on top of the same Python core:

- **Status bar** — live token usage at a glance (`⚡ 1,204 / 5,000 tokens`)
- **Inline hints** — hover over a selection to see estimated cost before sending
- **Budget alerts** — warning popup when you're approaching your limit
- **Command palette** — `TokenCUNT: Analyze File`, `TokenCUNT: Show Report`
- **Side panel** — full session breakdown by task

---

## Contributing

Built by a student, for developers who actually care about not burning credits. PRs and issues welcome.

---

## License

MIT
