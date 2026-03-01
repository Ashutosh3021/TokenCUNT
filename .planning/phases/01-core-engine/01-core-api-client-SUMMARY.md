---
phase: 01-core-engine
plan: 01
subsystem: core
tags: [api, retry, exceptions]
dependency_graph:
  requires: []
  provides: [MiniMaxApiClient, exceptions]
  affects: [all]
tech_stack:
  added: [httpx, tenacity]
  patterns: [async, retry, exponential-backoff]
key_files:
  created:
    - src/tokencunt/core/api_client.py
    - src/tokencunt/core/exceptions.py
    - pyproject.toml
decisions:
  - "httpx for async HTTP"
acity for retry logic"
---

# Phase 1 Plan 1  - "ten: API Client with Retry Logic Summary

**One-liner:** MiniMax API client with 3-retry exponential backoff and custom exception hierarchy

## Completed Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create custom exception classes | 068302a | src/tokencunt/core/exceptions.py |
| 2 | Create MiniMax API client with retry logic | 1a6df2e | src/tokencunt/core/api_client.py |
| 3 | Export modules in __init__.py | 1a6df2e | src/tokencunt/core/__init__.py |

## Artifacts Created

- `src/tokencunt/core/exceptions.py` — Custom exception classes:
  - `TokenCUNTApiError` (base with status, message, suggested_fix)
  - `TokenCUNTAuthError` (401 errors)
  - `TokenCUNTRateLimitError` (429 errors)
  - `TokenCUNTClientError` (4xx errors)
  - `TokenCUNTTimeoutError` (timeout errors)

- `src/tokencunt/core/api_client.py` — API client:
  - `MiniMaxApiClient` with async httpx
  - 3 retries with exponential backoff (1s→2s→4s)
  - `chat()` method for chat completions
  - `ApiResponse` with content, usage, model, id

## Verification

- [x] All exception classes importable
- [x] MiniMaxApiClient has chat() method
- [x] Retry decorator applied to request method
- [x] Custom exceptions raised for appropriate HTTP errors

## Deviation Documentation

**None** — Plan executed exactly as written.

## Phase Goal Progress

- REQ-01: ✅ API client must connect to MiniMax API
