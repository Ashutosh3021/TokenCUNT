# TokenCUNT — Project Definition

> A smart, token-efficient AI layer for developers. Built with Python + MiniMax M2.5 API.

---

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | TokenCUNT |
| **Type** | Developer Tool (CLI + VSCode Extension) |
| **Core** | Token-efficient AI interactions with MiniMax M2.5 |
| **Goal** | Minimize API costs while maintaining AI utility |

---

## Vision

Most AI developer tools waste credits through redundant calls, unnecessary context re-reading, and lack of usage visibility. TokenCUNT provides:

- **Efficiency by design** — smart batching and context management
- **Transparency** — real-time token cost visibility
- **Control** — configurable budgets, limits, and session rules

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
│  - Smart batcher                    │
│  - Budget enforcer                  │
│  - Prompt optimizer                 │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         MiniMax M2.5 API            │
└─────────────────────────────────────┘
```

---

## Core Modules

### Phase 1: Core Engine (Python)

| Module | Responsibility |
|--------|---------------|
| `api_client.py` | Handles all MiniMax API calls |
| `token_counter.py` | Counts tokens before and after each call |
| `budget.py` | Enforces token budgets, raises alerts |
| `batcher.py` | Combines multiple small requests into one |
| `optimizer.py` | Strips redundant context, compresses prompts |
| `session.py` | Tracks usage across a full session |

### Phase 2: CLI Tool

| Command | Purpose |
|---------|---------|
| `ts ask` | Ask a question with token tracking |
| `ts analyze` | Analyze a file and suggest changes |
| `ts batch` | Batch multiple tasks from a file |
| `ts report` | View usage report for current session |
| `ts session` | Set session budget |

### Phase 3: VSCode Extension

| Feature | Description |
|---------|-------------|
| Status bar | Live token usage display |
| Inline hints | Hover to see estimated token cost |
| Budget alerts | Warning popup when approaching limit |
| Command palette | Run TokenCUNT commands |
| Side panel | Full session usage breakdown |

---

## Technology Stack

### Core (Python)
- **httpx** — Async HTTP client for API calls
- **tiktoken** — Token counting
- **python-dotenv** — Environment configuration

### CLI
- **Typer** — CLI framework
- **Rich** — Beautiful terminal output

### VSCode Extension (TypeScript)
- **VS Code API** — Extension framework

---

## Key Features

- **Dry run mode** — Count tokens before sending
- **Token budgets** — Set limits per session
- **Smart batching** — Combine multiple requests
- **Session reports** — Summary of all usage
- **Real-time tracking** — Live token count display

---

## First Steps

1. Set up Python project with `pyproject.toml`
2. Build `api_client.py` — Make simple MiniMax API call
3. Build `token_counter.py` — Count tokens before/after
4. Wire up `ts ask "hello"` — First CLI command
5. Add budget tracking

---

*Built for developers who care about not burning credits.*
