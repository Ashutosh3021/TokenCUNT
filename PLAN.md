# TokenCUNT — Project Plan
> A smart, token-efficient AI layer for developers. Built with Python + MiniMax M2.5 API.

---

## The Core Idea

Most AI tools waste credits — they make redundant calls, re-read context unnecessarily, and lack any visibility into usage. TokenCUNT fixes this by being:

- **Efficient by design** — minimizes API calls through smart batching and context management
- **Transparent** — shows you exactly how many tokens each operation costs
- **In control** — lets you set budgets, limits, and rules per session or task

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│         User Interface              │
│   CLI Tool  │  VSCode Extension     │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│           Core Engine               │
│  - Token counter & tracker          │
│  - Smart batcher                    │
│  - Budget enforcer                  │
│  - Prompt optimizer                 │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         MiniMax M2.5 API            │
└─────────────────────────────────────┘
```

The core engine is shared — the CLI and extension are just interfaces on top of it.

---

## Phase 1 — Core Engine (Python)

**Location:** `TokenCUNT/core/`

### Modules

| Module | Responsibility |
|--------|---------------|
| `api_client.py` | Handles all MiniMax API calls |
| `token_counter.py` | Counts tokens before and after each call |
| `budget.py` | Enforces token budgets, raises alerts |
| `batcher.py` | Combines multiple small requests into one |
| `optimizer.py` | Strips redundant context, compresses prompts |
| `session.py` | Tracks usage across a full session |

### Key Features
- Count tokens **before** sending (dry run mode)
- Set a **token budget** per session (e.g. 10,000 tokens max)
- **Batch** multiple requests automatically
- **Session report** — summary of all usage at the end

---

## Phase 2 — CLI Tool

**Name:** `TokenCUNT` (or shorthand `ts`)

**Install:**
```bash
pip install TokenCUNT
```

### Commands

```bash
# Ask a question with token tracking
ts ask "explain this function" --file main.py

# Dry run — see token cost before sending
ts ask "refactor this" --file app.py --dry-run

# Set a session budget
ts session --budget 5000

# View usage report for current session
ts report

# Analyze a file and suggest changes (like ReactDoctor)
ts analyze --file main.py

# Batch multiple tasks from a file
ts batch --tasks tasks.txt
```

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

### Project Structure
```
TokenCUNT/
├── core/
│   ├── api_client.py
│   ├── token_counter.py
│   ├── budget.py
│   ├── batcher.py
│   ├── optimizer.py
│   └── session.py
├── cli/
│   ├── main.py          ← entry point (uses Typer)
│   └── commands/
│       ├── ask.py
│       ├── analyze.py
│       ├── batch.py
│       └── report.py
├── config/
│   └── settings.py      ← API key, default budget, model config
├── tests/
└── README.md
```

### Tech Stack
- **Typer** — CLI framework (clean, modern)
- **Rich** — beautiful terminal output
- **httpx** — async HTTP client for API calls
- **tiktoken** — token counting

---

## Phase 3 — VSCode Extension

**Name:** `TokenCUNT for VS Code`  
**File:** `TokenCUNT-vscode/` (separate folder, TypeScript)

> Built after CLI is stable. Calls the Python core as a backend subprocess or local server.

### Features

- **Status bar** — shows live token usage (e.g. `⚡ 1,204 / 5,000 tokens`)
- **Inline hints** — hover over a selection to see estimated token cost before sending
- **Budget alerts** — warning popup when approaching limit
- **Command palette** — run `TokenCUNT: Analyze File`, `TokenCUNT: Show Report`
- **Side panel** — full session usage breakdown by task

### How it connects to Python core
The extension spins up the Python CLI as a local background process and communicates via stdin/stdout or a lightweight local HTTP server (Flask/FastAPI).

### Extension Structure
```
TokenCUNT-vscode/
├── src/
│   ├── extension.ts     ← entry point
│   ├── statusBar.ts
│   ├── coreClient.ts    ← talks to Python backend
│   └── commands.ts
├── package.json
└── README.md
```

---

## Build Roadmap

| Phase | What | Status |
|-------|------|--------|
| 1 | Core engine (Python) | 🔲 Not started |
| 2 | CLI tool with `ask` and `report` commands | 🔲 Not started |
| 3 | Add `analyze` and `batch` commands | 🔲 Not started |
| 4 | VSCode extension (status bar + basic commands) | 🔲 Not started |
| 5 | VSCode side panel + inline hints | 🔲 Not started |

---

## API Config (MiniMax M2.5)

```python
# config/settings.py
API_KEY = "<your-minimax-key-from-opencode>"
API_BASE_URL = "https://api.minimax.chat/v1"
MODEL = "abab6.5-chat"   # MiniMax M2.5
DEFAULT_BUDGET = 10000   # tokens per session
```

---

## First Step to Build

1. Set up the Python project with `pyproject.toml`
2. Build `api_client.py` — make a simple call to MiniMax API
3. Build `token_counter.py` — count tokens before/after
4. Wire up the first CLI command: `ts ask "hello"`
5. Add budget tracking on top

---

*Built by a student, for developers who care about not burning credits.*