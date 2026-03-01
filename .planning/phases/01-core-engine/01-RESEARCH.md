# Phase 1: Core Engine — Research

> Technical findings for building the Python core modules.

---

## MiniMax API Integration

### API Compatibility

MiniMax provides **OpenAI-compatible API** endpoints, making integration straightforward:

| Aspect | Details |
|--------|---------|
| **Base URL** | `https://api.minimax.io/v1` |
| **Authentication** | Bearer token: `Authorization: Bearer YOUR_API_KEY` |
| **Required Header** | `GroupId` (via query parameter or header) |
| **Models** | `MiniMax-M2.5`, `MiniMax-M2.5-highspeed`, `MiniMax-M2.1`, etc. |

### Quick Integration Pattern

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.io/v1"
)

response = client.chat.completions.create(
    model="MiniMax-M2.5",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ]
)
```

### Rate Limits

| Tier | TPM (Tokens/Min) | RPM (Requests/Min) |
|------|------------------|---------------------|
| Free | 10,000 | 60 |
| Paid | Higher (contact for quota) |

**Best Practices:**
- Use worker queues with concurrency control (3-5 in flight)
- Back off on 429 with exponential backoff + jitter
- Cache deterministic prompts
- Monitor `x-ratelimit-remaining` headers

### Error Handling

| Status Code | Meaning | Retry? |
|-------------|---------|--------|
| 400 | Bad request | No |
| 401 | Auth failure | No |
| 429 | Rate limited | Yes (with backoff) |
| 500+ | Server error | Yes |

---

## HTTP Client Patterns (httpx)

### Why httpx?

- Modern async support
- Consistent sync/async API
- Better than `requests` for new projects
- Built-in connection pooling

### Retry Strategy (per CONTEXT.md)

**3 retries with exponential backoff: 1s → 2s → 4s**

Using `tenacity` library:

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def make_request(client: httpx.AsyncClient, url: str, **kwargs):
    return await client.post(url, **kwargs)
```

### Key Points

- **Retry only on:** 5xx errors, timeouts, network errors
- **Do NOT retry:** 400, 401, 403, 422
- **Respect `Retry-After` header** when present
- **Add jitter** to prevent thundering herd

---

## Token Counting (tiktoken)

### Installation

```bash
pip install tiktoken
```

### Basic Usage

```python
import tiktoken

# For OpenAI models (works for estimation)
encoding = tiktoken.encoding_for_model("gpt-4")

# Or use specific encoding
encoding = tiktoken.get_encoding("cl100k_base")

tokens = encoding.encode("Hello, world!")
token_count = len(tokens)
```

### MiniMax Tokenization

MiniMax uses **cl100k_base** encoding (same as GPT-4). Use this for estimation:

```python
def estimate_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
```

### Chat Message Token Counting

```python
def count_message_tokens(messages: list, model: str = "gpt-4") -> int:
    """Count tokens for chat messages (includes formatting overhead)."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens_per_message = 3  # <|im_start|>, role, <|im_end|>
    tokens = 0
    
    for message in messages:
        tokens += tokens_per_message
        tokens += len(encoding.encode(message.get("content", "")))
        tokens += len(encoding.encode(message.get("role", "")))
    
    return tokens
```

### Performance Notes

- For large texts, use `encode_to_numpy()` to reduce memory
- Approximation: `len(text) // 4` works for rough estimates
- Target: <100ms for estimation (PERF-01)

---

## Configuration Management

### Recommended Stack

| Tool | Purpose |
|------|---------|
| `pydantic-settings` | Type-safe config loading |
| `PyYAML` | YAML file parsing |
| `python-dotenv` | .env file support |

### Installation

```bash
pip install pydantic-settings pyyaml python-dotenv
```

### Priority Order (per CONTEXT.md)

1. **Environment variables** (highest priority)
2. **Config file** (`~/.tokencunt/config.yaml`)
3. **Hardcoded defaults** (lowest priority)

### Config File Location

```
~/.tokencunt/config.yaml
```

### Implementation Pattern

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import yaml

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MINIMAX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    api_key: str = Field(default="")
    default_model: str = Field(default="MiniMax-M2.5")
    default_budget: int = Field(default=100000)  #_dir: Path = tokens
    session Field(default_factory=lambda: Path.home() / ".tokencunt" / "sessions")

settings = AppSettings()
```

### Validation Command

Per CONTEXT.md: `ts config validate` to check setup.

---

## Session Persistence

### Storage Format

Per CONTEXT.md: **JSON files** in `~/.tokencunt/sessions/`

### File Structure

```
~/.tokencunt/
├── config.yaml          # User configuration
└── sessions/
    ├── session-001.json  # Session data
    ├── session-002.json
    └── ...
```

### Session Data Model

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

class RequestRecord(BaseModel):
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    estimated_tokens: Optional[int] = None
    prompt: str
    response: Optional[str] = None

class Session(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    requests: list[RequestRecord] = []
    total_usage: TokenUsage = TokenUsage()
    
    @property
    def request_count(self) -> int:
        return len(self.requests)
```

### Save/Load Pattern

```python
import json
from pathlib import Path
from datetime import datetime

class SessionManager:
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: Session):
        filepath = self.session_dir / f"{session.session_id}.json"
        with open(filepath, "w") as f:
            json.dump(session.model_dump(mode="json"), f, indent=2, default=str)
    
    def load_session(self, session_id: str) -> Optional[Session]:
        filepath = self.session_dir / f"{session_id}.json"
        if not filepath.exists():
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        return Session(**data)
    
    def create_session(self) -> Session:
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        return Session(
            session_id=session_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
```

---

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| HTTP Client | httpx | Async support, modern API |
| Retry Logic | tenacity | Industry standard, flexible |
| Token Library | tiktoken | Fast, accurate for OpenAI-compatible |
| Config | pydantic-settings | Type-safe, multi-source |
| Session Storage | JSON files | Simple, portable, per CONTEXT.md |
| Encoding | cl100k_base | Same as MiniMax models |

---

## Dependencies

```txt
httpx>=0.27.0
tiktoken>=0.7.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
tenacity>=8.0.0
```

---

*Research complete. Ready for planning.*
