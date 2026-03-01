# TokenCUNT — Technology Stack

> Technologies selected for building the token-efficient AI layer.

---

## Core Python

| Library | Purpose | Version |
|---------|---------|---------|
| **httpx** | Async HTTP client for MiniMax API calls | ^0.25.0 |
| **tiktoken** | Token counting (OpenAI-compatible) | ^0.5.0 |
| **python-dotenv** | Environment variable management | ^1.0.0 |

---

## CLI Framework

| Library | Purpose | Version |
|---------|---------|---------|
| **Typer** | Modern CLI framework with0.9. type hints | ^0 |
| **Rich** | Rich terminal output and formatting | ^13.7.0 |

---

## VSCode Extension

| Technology | Purpose |
|------------|---------|
| **TypeScript** | Extension language |
| **VS Code API** | Extension framework |

---

## API Integration

| Service | Endpoint | Model |
|---------|----------|-------|
| MiniMax | `https://api.minimax.chat/v1` | `abab6.5-chat` |

---

## Development Tools

| Tool | Purpose |
|------|---------|
| **pytest** | Testing framework |
| **black** | Code formatting |
| **mypy** | Type checking |
| **ruff** | Linting |

---

## Project Structure

```
TokenCUNT/
├── core/               # Core engine modules
│   ├── api_client.py
│   ├── token_counter.py
│   ├── budget.py
│   ├── batcher.py
│   ├── optimizer.py
│   └── session.py
├── cli/                # CLI tool
│   ├── main.py
│   └── commands/
├── TokenCUNT-vscode/   # VSCode extension
├── config/
│   └── settings.py
└── tests/
```

---

*Stack selected for efficiency, developer experience, and cost-effectiveness.*
