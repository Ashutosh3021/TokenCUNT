# Phase 1: Core Engine — Context

> Design decisions from discuss-phase for the Python core modules.

---

## Decisions

### Error Handling

| Decision | Choice |
|----------|--------|
| Exception types | Custom exception classes (`TokenCUNTApiError`, `TokenCUNTAuthError`, `TokenCUNTRateLimitError`, `TokenCUNTClientError`) |
| Retry strategy | 3 retries with exponential backoff (1s → 2s → 4s) |
| Rate limit handling | Wait and retry automatically, respect `Retry-After` header |
| Error messages | Include status, message, AND suggested fix |

### Configuration

| Decision | Choice |
|----------|--------|
| API key storage | Both env var (`MINIMAX_API_KEY`) and config file (`~/.tokencunt/config.yaml`) |
| Priority order | Env vars → Config file → Hardcoded defaults |
| CLI command | `ts config validate` to check setup |
| Session persistence | JSON files in `~/.tokencunt/sessions/` |

### Module API Design

| Decision | Choice |
|----------|--------|
| Primary interface | Session object — `session = TokenCUNT()` |
| Package import | Single import: `from tokencunt import TokenCUNT` |
| Token counting | Integrated — api_client automatically counts tokens |
| Budget enforcement | Opt-in — must explicitly enable budget checking |

### Response Handling

| Decision | Choice |
|----------|--------|
| Response format | Parsed response object with `.content`, `.usage`, `.model`, `.id` |
| Token usage | Structured object: `response.usage.input_tokens`, `response.usage.output_tokens` |
| Dry-run mode | Same response object with `.estimated_tokens` filled, `.content = None` |
| Streaming | Optional `.stream()` method for long outputs |

---

## Deferred Ideas

*No deferred ideas for this phase.*

---

## Claude's Discretion

The following are left to implementation judgment:

- **Exception hierarchy** — Exact structure of exception classes (base class, inheritance)
- **Config file format** — YAML vs JSON for `~/.tokencunt/config.yaml`
- **Session details** — Session ID generation, file naming convention
- **Streaming** — Exact API for `.stream()` method

---

## Requirements

| ID | Requirement |
|----|-------------|
| REQ-01 | API client must connect to MiniMax API |
| REQ-02 | Token counter must estimate before API calls |
| REQ-03 | Token counter must track actual usage |
| REQ-04 | Budget manager must enforce session limits |
| REQ-05 | Budget manager must alert at 80% threshold |
| REQ-06 | Batcher must combine multiple requests |
| REQ-07 | Optimizer must reduce prompt size |
| REQ-08 | Session must track all operations |

---

## Modules

| Module | Responsibility |
|--------|---------------|
| `core/api_client.py` | Handles MiniMax API calls with retry logic |
| `core/token_counter.py` | Estimates and tracks token usage |
| `core/budget.py` | Enforces token budgets (opt-in) |
| `core/batcher.py` | Combines multiple requests |
| `core/optimizer.py` | Reduces prompt size |
| `core/session.py` | Tracks usage across session |

---

*Context defined. Ready for planning.*
