# Phase 2: CLI Tool — Context

> User decisions from discuss-phase.

---

## Phase Overview

**Name:** CLI Tool
**Domain:** Building command-line interface using Typer + Rich
**Commands:** ask, analyze, batch, report, session
**Existing:** Core modules from Phase 1 (api_client, token_counter, budget, session)

---

## Decisions

### Command Interface

- **Structure:** Single `ts` entry point with subcommands
- **Commands:** `ts ask`, `ts analyze`, `ts batch`, `ts report`, `ts session`
- **File input:** Both `-f/--file PATH` and positional arguments supported

### Output Formatting

- **Library:** Rich panels, tables, syntax highlighting
- **Verbosity levels:**
  - `-q, --quiet` — Only essential output (response text)
  - Default — Normal with token info
  - `-v, --verbose` — Full debug info
- **JSON flag:** `--json` for machine-readable output (all commands)

### User Experience

- **Dry-run:** Default enabled (show estimated tokens before sending)
- **Interactive:** Flags-first approach
  - `--yes` / `-y` for confirmations
  - `--no-interactive` to disable prompts entirely

### Error Handling

- **Format:** Rich-formatted error messages with suggestions
- **Exit codes:**
  - 0 — Success
  - 1 — General error
  - 2 — Invalid arguments
  - 3 — Budget exceeded
  - 130 — Keyboard interrupt
- **Debug mode:** `--debug` flag shows full traceback

---

## CLI Commands

| Command | Description | Key Flags |
|---------|-------------|------------|
| `ts ask` | Ask question with token tracking | `--file`, `--dry-run`, `--json` |
| `ts analyze` | Analyze file for improvements | `--file`, `--dry-run`, `--json` |
| `ts batch` | Process multiple tasks | `--file`, `--dry-run`, `--json` |
| `ts report` | Show session usage report | `--json`, `--format` |
| `ts session` | Manage session settings | `--budget`, `--model` |

---

## Global Flags

| Flag | Description |
|------|-------------|
| `-q, --quiet` | Minimal output |
| `-v, --verbose` | Debug output |
| `--json` | JSON output |
| `--debug` | Debug mode with traceback |
| `--config PATH` | Custom config file |
| `-y, --yes` | Skip confirmations |

---

## Requirements Addressed

From REQUIREMENTS.md:

- REQ-09: CLI must have `ask` command
- REQ-10: CLI must support `--dry-run` flag
- REQ-11: CLI must have `analyze` command
- REQ-12: CLI must have `batch` command
- REQ-13: CLI must have `report` command
- REQ-14: CLI must have `session` command
- REQ-15: CLI must display token costs
- REQ-16: CLI must show budget status

---

## Dependencies

- Phase 1 core modules: `api_client`, `token_counter`, `budget`, `session`
- New dependencies: `typer`, `rich`

---

*Context locked. Ready for planning.*
