# TokenCUNT

![Python Version](https://img.shields.io/badge/python-1.20.1-blue)
![Version](https://img.shields.io/badge/version-1.20.1-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Status](https://img.shields.io/badge/status-In%20Progress-orange)
[![Download VSIX](https://img.shields.io/badge/Download-VSIX-blue?logo=visual-studio-code)](tokencunt-vscode/tokencunt-0.1.0.vsix)

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

### VSCode Extension

Download and install the VSCode extension:

```bash
# Option 1: Install from VSIX file
code --install-extension tokencunt-vscode/tokencunt-0.1.0.vsix

# Option 2: Manual install
# 1. Open VSCode
# 2. Go to Extensions (Ctrl+Shift+X)
# 3. Click "..." menu → "Install from VSIX"
# 4. Select tokencunt-0.1.0.vsix
```

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

### Phase 4: Advanced Features

| Command | Description |
|---------|-------------|
| `ts scan <path>` | Scan project for token estimation |
| `ts scan --extensions py,js --verbose` | Scan with specific extensions |
| `ts scan --ignore .tokencuntignore` | Scan with custom ignore file |
| `ts simulate --requests 1000 --tokens 500` | Simulate API costs |
| `ts simulate --scenario startup --model gpt-4` | Use pre-defined scenario |
| `ts simulate --users 100 --messages 50 --tokens 300` | User-based scenario |
| `ts diff original.txt optimized.txt` | Git-style prompt diff |
| `ts diff --stats` | Show only statistics |
| `ts optimize prompt.txt` | Optimize with AI + rules |
| `ts optimize prompt.txt --rules-only` | Rules-only optimization |
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
| 3 | VSCode Extension | ✅ Done |
| 4 | Advanced Features (scan, simulate, diff, optimize) | ✅ Done |

---

## Pro Tips for Maximum Leverage

### 1. Use `ts scan` Before Starting New Projects

```bash
# Get a baseline of your project size
ts scan ./src

# Know your context window limits
# Large projects = split into smaller prompts
```

### 2. Set Budget Alerts Early

```bash
# Set a monthly budget
ts session config --budget 50000

# The extension will warn you at 80%
# You can stop before hitting the limit
```

### 3. Use `ts diff` to Compare Prompt Strategies

```bash
# Compare verbose vs concise prompts
ts diff verbose_prompt.txt concise_prompt.txt

# See exactly how much you're saving
# Use the optimized version in production
```

### 4. Optimize with Rules-First (Free!)

```bash
# Rules-only is instant and free
ts optimize prompt.txt --rules-only

# Then enhance with AI if needed
ts optimize optimized.txt --ai-only --show-diff
```

### 5. Simulate Before Scaling

```bash
# Before launching to 1000 users
ts simulate --users 1000 --messages 100 --tokens 500 --model gpt-4

# Know your monthly burn rate
# Adjust model to fit budget
```

### 6. Use the VSCode Extension for Quick Analysis

- **Analyze selected code** — Select code → right-click → TokenCUNT: Analyze
- **Quick prompts** — Use command palette for fast access
- **Status bar** — Always know your current session usage

### 7. Batch Similar Tasks

```bash
# Create tasks.json
# {
#   "tasks": [
#     {"prompt": "Explain function 1", "file": "src/a.py"},
#     {"prompt": "Explain function 2", "file": "src/b.py"}
#   ]
# }

ts batch --file tasks.json --parallel
```

### 8. Use `--dry-run` for Cost Previewing

```bash
# Always check cost first
ts ask "refactor this entire file" --file huge.py --dry-run

# If too expensive, break into smaller chunks
ts ask "refactor first 50 lines" --file huge.py
```

---

## Example Workflows

### Daily Development
```bash
# Morning: Check budget
ts report

# During: Analyze before asking
ts analyze --file problem.py --focus bugs

# Ask with tracking
ts ask "fix this bug" --file problem.py

# End: Review spending
ts report
```

### Project Token Audit
```bash
# 1. Scan entire project
ts scan ./src --verbose

# 2. Simulate your usage pattern
ts simulate --scenario startup --model minimax

# 3. Optimize your most-used prompts
ts optimize common_prompts.txt --rules-only --output optimized/

# 4. Diff to compare
ts diff common_prompts.txt optimized/common.txt
```

### Production Cost Control
```bash
# 1. Set strict budget
ts session config --budget 10000

# 2. Use cheaper models for simple tasks
ts analyze --file simple.py --model minimax

# 3. Reserve GPT-4 for complex tasks
ts ask "complex refactor" --file hard.py --model gpt-4
```

---

## FAQ

### What exact problem does TokenCUNT solve?

TokenCUNT solves the problem of **uncontrolled API costs** when using AI models. Most developers have no visibility into how many tokens their prompts consume, leading to surprise bills at the end of the month. TokenCUNT provides:

- **Pre-call estimation** — Know token cost BEFORE making API calls
- **Budget enforcement** — Hard limits prevent runaway spending
- **Usage transparency** — Real-time tracking of all API usage
- **Session history** — Know exactly what you spent each session

### Who is the primary user?

- **AI developers** building apps with LLMs
- **SaaS builders** integrating AI into products
- **Students** learning about LLMs on limited budgets
- **Freelancers** managing client API budgets

### What input does the user give?

- **Raw text** — Direct prompts
- **Files** — `.txt`, `.py`, `.js`, `.md`, or any text file
- **Multiple files** — Via batch processing

### What output does the tool return?

- **Token count** — Before and after API calls
- **Cost estimation** — Based on model pricing
- **Session reports** — Detailed breakdown of usage

### Which models are supported?

Currently: **MiniMax** models (abab6.5-chat family)

Future support planned:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google Gemini

### Does it support multiple tokenizers?

Yes — uses **tiktoken** which supports multiple encodings:
- cl100k_base (GPT-4, Claude, etc.)
- p50k_base (GPT-3)
- r50k_base (GPT-2)

### What makes TokenCUNT better than existing token counters?

1. **Pre-call estimation** — Most counters only count AFTER the call
2. **Budget enforcement** — Most counters only track, don't prevent overspending
3. **Integrated CLI** — Ready to use, not just a library
4. **IDE integration** — VSCode extension with inline hints

### Future features planned?

- Cost alerts via webhooks
- Multi-user team dashboards
- Integration with more IDEs (JetBrains, Neovim)

---

## Contributing

Built by a student, for developers who actually care about not burning credits. PRs and issues welcome.

---

## License

MIT
