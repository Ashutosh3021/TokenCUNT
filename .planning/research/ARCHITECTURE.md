# TokenCUNT — Architecture

> System design and component interactions.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  ┌─────────────────┐           ┌─────────────────────────┐  │
│  │   CLI Tool      │           │   VSCode Extension      │  │
│  │   (Typer)       │           │   (TypeScript)          │  │
│  └────────┬────────┘           └────────────┬────────────┘  │
└───────────┼───────────────────────────────────┼──────────────┘
            │                                   │
            │      ┌─────────────────────┐     │
            └──────┤     Core Engine      ├─────┘
                   │     (Python)         │
                   └────────────┬──────────┘
                                │
                   ┌────────────▼──────────┐
                   │    MiniMax API         │
                   │    (abab6.5-chat)      │
                   └────────────────────────┘
```

---

## Component Diagram

### Core Engine

```
┌─────────────────────────────────────────────────────────────┐
│                        Core Engine                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │ api_client  │◄──►│token_counter│◄──►│   budget     │   │
│  └──────┬──────┘    └─────────────┘    └─────────────┘   │
│         │                                                 │
│         ▼                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  batcher    │◄──►│  optimizer  │◄──►│  session    │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Responsibilities

### api_client.py
- **Manages** HTTP connections to MiniMax API
- **Handles** request/response serialization
- **Implements** retry logic and error handling
- **Exports**: `MiniMaxClient` class

### token_counter.py
- **Estimates** token count before API calls
- **Tracks** actual tokens used in responses
- **Caches** counts for repeated prompts
- **Exports**: `TokenCounter` class

### budget.py
- **Enforces** session token limits
- **Monitors** usage against budget
- **Triggers** alerts at thresholds
- **Exports**: `BudgetManager` class

### batcher.py
- **Collects** multiple requests
- **Combines** requests efficiently
- **Executes** batched operations
- **Exports**: `RequestBatcher` class

### optimizer.py
- **Trims** unnecessary context
- **Compresses** prompts
- **Manages** conversation history
- **Exports**: `PromptOptimizer` class

### session.py
- **Tracks** session state
- **Records** all operations
- **Generates** usage reports
- **Exports**: `Session` class

---

## CLI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Entry Point                        │
│                         (main.py)                            │
│                      Uses: Typer                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ ask.py     │  │ analyze.py │  │ batch.py   │
└────────────┘  └────────────┘  └────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       ▼
              ┌────────────────┐
              │  Core Engine  │
              └────────────────┘
```

---

## VSCode Extension Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Extension Entry Point                     │
│                      (extension.ts)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    ▼                  ▼                  ▼
┌──────────┐    ┌──────────┐      ┌──────────┐
│statusBar │    │ commands │      │coreClient│
└──────────┘    └──────────┘      └────┬─────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │ Python Backend │
                               │ (CLI subprocess│
                               │  or HTTP)      │
                               └────────────────┘
```

---

## Data Flow

### Ask Command Flow

```
User Input → CLI Parser → Core Engine → API Client → MiniMax API
                                        ↓
                              Token Counter (track)
                                        ↓
                              Session (record)
                                        ↓
                              CLI Output → User
```

### Token Estimation Flow

```
User Input → Token Counter (estimate) → CLI Output (preview)
                                       ↓
                              If confirmed → API Call
```

---

## Configuration

### Settings Structure (config/settings.py)

```python
API_KEY = os.getenv("MINIMAX_API_KEY")
API_BASE_URL = "https://api.minimax.chat/v1"
MODEL = "abab6.5-chat"
DEFAULT_BUDGET = 10000
MAX_BATCH_SIZE = 10
TIMEOUT_SECONDS = 30
```

---

## Extension Communication

The VSCode extension communicates with the Python core via:

1. **Subprocess** — Spawn Python CLI as background process
2. **stdin/stdout** — JSON-RPC style messaging
3. **Local HTTP Server** — Optional Flask/FastAPI wrapper

---

*Architecture designed for modularity, testability, and extensibility.*
