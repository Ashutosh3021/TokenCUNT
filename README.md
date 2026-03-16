# TokenCUNT

![Python Version](https://img.shields.io/badge/python-3.10+-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
[![PyPI](https://img.shields.io/badge/PyPI-tokencunt-blue)](https://pypi.org/project/tokencunt/)
[![Downloads](https://img.shields.io/badge/downloads-1.0.0-green)](https://pypi.org/project/tokencunt/)
[![Download VSIX](https://img.shields.io/badge/Download-VSIX-blue?logo=visual-studio-code)](tokencunt-vscode/tokencunt-1.38.1.vsix)

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
# Install TokenCUNT CLI (recommended)
pip install tokencunt[cli]

# Or install in development mode
pip install -e ".[cli,dev]"
```

### Requirements

- Python 3.10+
- MiniMax API key

### VSCode Extension

Download and install the VSCode extension:

```bash
# Install from VSIX file
code --install-extension tokencunt-vscode/tokencunt-1.38.1.vsix
```

Or manually:
1. Open VSCode
2. Go to Extensions (Ctrl+Shift+X)
3. Click "..." menu → "Install from VSIX"
4. Select `tokencunt-1.38.1.vsix`

**VSCode Extension Features:**
- Status bar with live token count
- Inline hover hints for token estimation
- Command palette integration
- Budget alerts when approaching limit
- Quick actions via Ctrl+Shift+P

---

## Quick Start

### 1. Configure your API key

```bash
# Set environment variable (Linux/Mac)
export MINIMAX_API_KEY="your-api-key"
export MINIMAX_GROUP_ID="your-group-id"

# Set environment variable (Windows)
set MINIMAX_API_KEY=your-api-key
set MINIMAX_GROUP_ID=your-group-id

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
ts ask "refactor this" --file app.py --dry-run

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

### Core Commands

| Command | Description |
|---------|-------------|
| `ts start` | Show logo and welcome message |
| `ts ask "<prompt>" --file <file>` | Ask a question with token tracking |
| `ts ask ... --dry-run` | Preview token cost without API call |
| `ts analyze --file <file>` | Analyze a file for improvements |
| `ts analyze --file <file> --focus bugs` | Focus on bugs, performance, style, or security |
| `ts batch --file <json>` | Run multiple tasks from JSON file |
| `ts report` | Show session usage breakdown |
| `ts report --json` | JSON output for scripting |
| `ts version` | Show version information |

### Session Management

| Command | Description |
|---------|-------------|
| `ts session new` | Create a new session |
| `ts session list` | List all sessions |
| `ts session config --budget 5000` | Set token budget |
| `ts session clear` | Clear session data |

### Advanced Features

| Command | Description |
|---------|-------------|
| `ts scan <path>` | Scan project for token estimation |
| `ts scan --extensions py,js --verbose` | Scan with specific extensions |
| `ts scan --ignore .tokencuntignore` | Custom ignore file |
| `ts simulate --requests 1000 --tokens 500` | Simulate API costs |
| `ts simulate --scenario startup --model abab6.5` | Pre-defined scenario |
| `ts simulate --users 100 --messages 50 --tokens 300` | User-based scenario |
| `ts diff original.txt optimized.txt` | Git-style prompt diff |
| `ts diff --stats` | Show only statistics |
| `ts optimize prompt.txt` | Optimize with AI + rules |
| `ts optimize prompt.txt --rules-only` | Rules-only (free & instant) |
| `ts optimize --show-diff` | Show changes made |

### Global Options

| Option | Description |
|--------|-------------|
| `-q, --quiet` | Minimal output |
| `-v, --verbose` | Verbose output |
| `--json` | JSON output |
| `--debug` | Debug mode with traceback |
| `-y, --yes` | Skip confirmations |

---

## Example Output

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
│   CLI Tool  │  VSCode Extension    │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│           Core Engine              │
│  - Token counter & tracker        │
│  - Smart batcher                  │
│  - Budget enforcer                │
│  - Prompt optimizer                │
│  - Scanner & Simulator            │
│  - Diff & Compare                 │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         MiniMax M2.5 API           │
└─────────────────────────────────────┘
```

The core engine is shared — CLI and VSCode extension are just interfaces on top of it.

---

## Project Structure

```
TokenCUNT/
├── src/tokencunt/               # Main package
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── cli/                     # CLI interface
│   │   ├── app.py               # Typer entry point
│   │   ├── logo.py              # ASCII logo
│   │   ├── formatters.py        # Rich output
│   │   └── commands/            # CLI commands
│   │       ├── ask.py
│   │       ├── analyze.py
│   │       ├── batch.py
│   │       ├── report.py
│   │       ├── session.py
│   │       ├── scan.py
│   │       ├── simulate.py
│   │       ├── diff.py
│   │       └── optimize.py
│   └── core/                    # Core engine
│       ├── __init__.py
│       ├── api_client.py        # MiniMax API
│       ├── token_counter.py    # Token counting
│       ├── budget.py            # Budget enforcement
│       ├── batcher.py           # Smart batching
│       ├── optimizer.py        # Prompt optimization
│       ├── session.py          # Session tracking
│       ├── scanner.py          # Project scanner
│       ├── simulator.py        # Cost simulator
│       ├── differ.py           # Prompt differ
│       └── exceptions.py       # Custom exceptions
├── tokencunt-vscode/           # VSCode extension
│   ├── src/                    # TypeScript source
│   ├── out/                    # Compiled JS
│   └── tokencunt-1.38.1.vsix   # Extension package
├── pyproject.toml              # Package config
└── README.md
```

---

## Tech Stack

| Tool | Role |
|------|------|
| [Typer](https://typer.tiangolo.com/) | CLI framework |
| [Rich](https://github.com/Textualize/rich) | Terminal output |
| [httpx](https://www.python-httpx.org/) | Async HTTP client |
| [tiktoken](https://github.com/openai/tiktoken) | Token counting |
| [Tenacity](https://tenacity.readthedocs.io/) | Retry logic |
| [Pydantic](https://pydantic.dev/) | Data validation |

---

## Configuration

### Environment Variables

```bash
# Linux/Mac
export MINIMAX_API_KEY=your-api-key
export MINIMAX_GROUP_ID=your-group-id

# Windows
set MINIMAX_API_KEY=your-api-key
set MINIMAX_GROUP_ID=your-group-id
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

1. Environment variables (highest)
2. Config file
3. Hardcoded defaults (lowest)

---

## Roadmap

| Phase | What | Status |
|-------|------|--------|
| 1 | Core engine (Python) | ✅ Done |
| 2 | CLI Tool | ✅ Done |
| 3 | VSCode Extension | ✅ Done |
| 4 | Advanced Features | ✅ Done |

---

## Pro Tips

### 1. Use `ts scan` Before New Projects

```bash
ts scan ./src
# Know your context window limits
```

### 2. Set Budget Alerts Early

```bash
ts session config --budget 50000
# Warning at 80%
```

### 3. Use `ts diff` to Compare Prompts

```bash
ts diff verbose.txt concise.txt
```

### 4. Optimize with Rules-First (Free!)

```bash
ts optimize prompt.txt --rules-only
```

### 5. Simulate Before Scaling

```bash
ts simulate --users 1000 --messages 100 --tokens 500
```

### 6. Use `--dry-run` for Cost Preview

```bash
ts ask "refactor all" --file huge.py --dry-run
```

---

## FAQ

### What problem does TokenCUNT solve?

TokenCUNT solves **uncontrolled API costs** with AI models:

- **Pre-call estimation** — Know cost BEFORE making calls
- **Budget enforcement** — Hard limits prevent overspending
- **Usage transparency** — Real-time tracking
- **Session history** — Know exactly what you spent

### Who is it for?

- AI developers building LLM apps
- SaaS builders integrating AI
- Students on limited budgets
- Freelancers managing client budgets

### Which models are supported?

Currently: **MiniMax** models (abab6.5-chat family)

### Future support?

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google Gemini

### What tokenizers?

Uses **tiktoken** supporting:
- cl100k_base (GPT-4, Claude)
- p50k_base (GPT-3)
- r50k_base (GPT-2)

---

## Contributing

PRs and issues welcome! Built by a student, for developers who care about not burning credits.

---

## License

MIT
