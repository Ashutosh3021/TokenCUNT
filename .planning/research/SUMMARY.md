# TokenCUNT — Research Summary

> Key findings from project research phase.

---

## Research Outcomes

### Technology Selection

| Category | Choice | Rationale |
|----------|--------|-----------|
| HTTP Client | httpx | Async support, modern API, retry built-in |
| Token Counting | tiktoken | OpenAI-compatible, widely used |
| CLI Framework | Typer | Type-safe, modern, Rich integration |
| Terminal Output | Rich | Beautiful CLI, progress indicators |
| VSCode | TypeScript | Native extension language |

### Architecture Decision

**Core Python → CLI/Extension as interfaces**

Rationale:
- Single source of truth for token logic
- Easy to test core in Python
- CLI and extension just wrap the core
- Can add more interfaces later (REST API, etc.)

---

## Key Insights

### 1. Token Efficiency Matters

- MiniMax API pricing is token-based
- Redundant calls add up quickly
- Pre-call estimation saves money
- Smart batching reduces overhead

### 2. Session Tracking is Essential

- Developers need visibility into usage
- Budget enforcement prevents surprises
- Reports help optimize workflows
- History enables analysis

### 3. Extension Must Be Lightweight

- VSCode extensions must be responsive
- Python backend should run as subprocess
- Minimize communication overhead
- Cache aggressively

---

## Dependencies

### Required Packages

```
httpx>=0.25.0
tiktoken>=0.5.0
python-dotenv>=1.0.0
typer>=0.9.0
rich>=13.7.0
```

### Dev Dependencies

```
pytest>=7.4.0
black>=23.0.0
mypy>=1.5.0
ruff>=0.1.0
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| MiniMax API changes | Abstract API calls, version detection |
| Token count inaccuracy | Cache + verify against actual |
| Extension performance | Async operations, caching |
| Budget edge cases | Buffer for estimation errors |

---

## Next Steps

1. Set up `pyproject.toml` with dependencies
2. Create core modules (api_client, token_counter)
3. Build minimal working CLI
4. Add budget and session tracking
5. Develop VSCode extension

---

*Research complete. Ready for implementation.*
