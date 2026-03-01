# TokenCUNT — Roadmap

> Implementation phases and plan structure.

---

## Project Overview

**Goal:** Build a token-efficient AI layer for developers using Python + MiniMax M2.5 API

**Phases:** 3

**Approach:** Quick (3-5 phases, 1-3 plans each)

---

## Phase 1: Core Engine

**Goal:** Build the Python core modules for API interaction, token tracking, and budget management

### Objectives

1. Set up Python project structure with `pyproject.toml`
2. Implement API client for MiniMax communication
3. Build token counter for estimation and tracking
4. Create budget manager for session limits
5. Add request batcher for efficiency
6. Build prompt optimizer for context reduction
7. Implement session tracker for usage history

### Modules

- `core/api_client.py`
- `core/token_counter.py`
- `core/budget.py`
- `core/batcher.py`
- `core/optimizer.py`
- `core/session.py`

### Plans

- [x] 01-01-PLAN.md — API client with retry logic
- [x] 01-02-PLAN.md — Token counting functionality
- [x] 01-03-PLAN.md — Budget and session management

---

## Phase 2: CLI Tool

**Goal:** Build the command-line interface with all user-facing commands

### Objectives

1. Set up Typer CLI framework
2. Implement `ask` command with dry-run
3. Implement `analyze` command
4. Implement `batch` command
5. Implement `report` command
6. Implement `session` command
7. Add Rich output formatting

### Commands

| Command | Description |
|---------|-------------|
| `ts ask` | Ask question with token tracking |
| `ts analyze` | Analyze file for improvements |
| `ts batch` | Process multiple tasks |
| `ts report` | Show session usage report |
| `ts session` | Manage session settings |

### Plans

- [ ] 02-cli-setup — Typer setup and basic structure
- [ ] 02-cli-commands — Implement all CLI commands

---

## Phase 3: VSCode Extension

**Goal:** Build VSCode extension for in-editor token tracking

### Objectives

1. Set up VSCode extension project
2. Implement status bar with live token count
3. Add inline hints for token estimation
4. Create budget alert system
5. Add command palette integration
6. Build side panel for detailed view

### Features

| Feature | Description |
|---------|-------------|
| Status Bar | Live token usage display |
| Inline Hints | Hover to see token cost |
| Budget Alerts | Warning at thresholds |
| Command Palette | Quick access to commands |
| Side Panel | Detailed session view |

### Plans

- [ ] 03-vscode-setup — Extension scaffolding
- [ ] 03-vscode-features — Implement all features

---

## Phase Timeline

| Phase | Focus | Complexity |
|-------|-------|------------|
| 1 | Core Engine | Medium |
| 2 | CLI Tool | Low |
| 3 | VSCode Extension | Medium |

---

## Dependencies

```
Phase 1 (Core)  →  No dependencies
Phase 2 (CLI)   →  Requires Phase 1
Phase 3 (VSCode) → Requires Phase 1
```

---

*Roadmap defined. Ready for execution.*
