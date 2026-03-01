---
phase: 01-core-engine
plan: 03
subsystem: core
tags: [budget, session, batcher, optimizer]
dependency_graph:
  requires: [TokenCounter]
  provides: [BudgetManager, SessionManager, RequestBatcher, PromptOptimizer, Config]
  affects: [cli]
tech_stack:
  added: [pydantic, pydantic-settings, pyyaml]
  patterns: [persistence, batching, optimization]
key_files:
  created:
    - src/tokencunt/config.py
    - src/tokencunt/core/session.py
    - src/tokencunt/core/budget.py
    - src/tokencunt/core/batcher.py
    - src/tokencunt/core/optimizer.py
decisions:
  - "JSON files for session persistence in ~/.tokencunt/sessions/"
  - "80% warning threshold for budget alerts"
---

# Phase 1 Plan 3: Budget, Session, Batcher, Optimizer Summary

**One-liner:** Complete core engine with budget enforcement, session persistence, request batching, and prompt optimization

## Completed Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create configuration module | 112d209 | src/tokencunt/config.py |
| 2 | Create session module | 112d209 | src/tokencunt/core/session.py |
| 3 | Create budget module | 112d209 | src/tokencunt/core/budget.py |
| 4 | Create batcher module | 112d209 | src/tokencunt/core/batcher.py |
| 5 | Create optimizer module | 112d209 | src/tokencunt/core/optimizer.py |
| 6 | Update __init__.py with all exports | 112d209 | src/tokencunt/core/__init__.py |

## Artifacts Created

- `src/tokencunt/config.py`:
  - Pydantic `Config` with priority: env vars → config file → defaults
  - Support for `~/.tokencunt/config.yaml`
  - `is_configured` property

- `src/tokencunt/core/session.py`:
  - `Session` model with request tracking
  - `SessionManager` with JSON persistence
  - `RequestRecord` for individual requests

- `src/tokencunt/core/budget.py`:
  - `BudgetManager` with 80% warning threshold
  - `BudgetStatus` enum (OK, WARNING, EXCEEDED)
  - `check_budget()` for pre-request validation

- `src/tokencunt/core/batcher.py`:
  - `RequestBatcher` to combine multiple requests
  - Token-based and count-based batching
  - `add()` and `flush()` methods

- `src/tokencunt/core/optimizer.py`:
  - `PromptOptimizer` for prompt reduction
  - Whitespace removal, duplicate sentence removal
  - Token truncation support

## Verification

- [x] Config loads from env, file, defaults (priority order)
- [x] Session saves/loads from JSON files
- [x] BudgetManager checks budget before requests
- [x] BudgetManager warns at 80% threshold
- [x] RequestBatcher combines multiple requests
- [x] PromptOptimizer reduces prompt size

## Deviation Documentation

**None** — Plan executed exactly as written.

## Phase Goal Progress

- REQ-04: ✅ Budget manager must enforce session limits
- REQ-05: ✅ Budget manager must alert at 80% threshold
- REQ-06: ✅ Batcher must combine multiple requests
- REQ-07: ✅ Optimizer must reduce prompt size
- REQ-08: ✅ Session must track all operations
