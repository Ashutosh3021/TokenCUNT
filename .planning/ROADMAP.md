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

- [x] 02-01-PLAN.md — Typer setup and basic structure
- [x] 02-02-PLAN.md — Implement all CLI commands

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

- [p] 03-01-PLAN.md — Extension scaffolding + CLI integration
- [p] 03-02-PLAN.md — Status bar + inline hints + commands
- [p] 03-03-PLAN.md — Setup flow webview + budget alerts

---

## Phase 4: Advanced Features

**Goal:** Add advanced developer tools for token optimization and cost management

### Objectives

1. **Repo Scanner** — Scan entire project for token estimation
2. **Cost Simulator** — Calculate monthly costs based on traffic
3. **Prompt Diff** — Git-style diff for prompt changes
4. **Prompt Optimizer** — AI + rule-based prompt optimization

### Commands

| Command | Description |
|---------|-------------|
| `ts scan` | Scan project directory for token estimation |
| `ts simulate` | Calculate monthly costs based on traffic |
| `ts diff` | Compare original vs optimized prompts |
| `ts optimize` | Optimize prompts for lower token count |

### Priority

1. **Repo Scanner** — Immediate value, easiest to implement
2. **Cost Simulator** — Turns tokens into business insight
3. **Prompt Diff** — Nice developer UX
4. **Prompt Optimizer** — Hardest feature

### Implementation Decisions

- **Prompt Optimizer:** AI + rule-based hybrid
- **Repo Scanner:** Configurable patterns + `.tokencuntignore`
- **Cost Simulator:** Support traffic estimates AND user scenarios
- **Prompt Diff:** Git-style diff output

### Plans

- [x] 04-01-PLAN.md — Repo Scanner
- [x] 04-02-PLAN.md — Cost Simulator
- [x] 04-03-PLAN.md — Prompt Diff
- [x] 04-04-PLAN.md — Prompt Optimizer

---

## Phase Timeline

| Phase | Focus | Complexity |
|-------|-------|------------|
| 1 | Core Engine | Medium |
| 2 | CLI Tool | Low |
| 3 | VSCode Extension | Medium |
| 4 | Advanced Features | Medium |

---

## Dependencies

```
Phase 1 (Core)      →  No dependencies
Phase 2 (CLI)       →  Requires Phase 1
Phase 3 (VSCode)     →  Requires Phase 1
Phase 4 (Advanced)   →  Requires Phase 1
```

---

*Roadmap defined. Ready for execution.*
