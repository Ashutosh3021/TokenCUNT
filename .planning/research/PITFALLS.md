# TokenCUNT — Common Pitfalls

> Things to avoid during development.

---

## API Integration

### ❌ Not handling rate limits
**Pitfall:** Ignoring MiniMax API rate limits causes request failures.

**Solution:** Implement exponential backoff and respect `Retry-After` headers.

```python
# Bad
response = client.post(url, json=data)

# Good
for attempt in range(max_retries):
    response = client.post(url, json=data)
    if response.status_code == 429:
        wait(response.headers.get("Retry-After", 2 ** attempt))
    else:
        break
```

### ❌ Hardcoding API keys
**Pitfall:** Storing API keys in source code.

**Solution:** Use environment variables only.

```python
# Bad
API_KEY = "sk-xxxxx"

# Good
API_KEY = os.getenv("MINIMAX_API_KEY")
```

---

## Token Counting

### ❌ Using wrong tokenizer
**Pitfall:** Using tiktoken with wrong model encoding.

**Solution:** Specify correct encoding for MiniMax model.

```python
# Bad
encoding = tiktoken.get_encoding("cl100k_base")

# Good (check MiniMax compatibility)
encoding = tiktoken.get_encoding("cl100k_base")  # Most compatible
```

### ❌ Not counting response tokens
**Pitfall:** Only counting input tokens.

**Solution:** Count both input and output tokens.

---

## Budget Management

### ❌ Not checking budget before API call
**Pitfall:** Exceeding budget silently.

**Solution:** Check and warn before every API call.

```python
# Bad
response = client.chat(prompt)

# Good
if session.tokens_used + estimated > budget:
    raise BudgetExceededError()
response = client.chat(prompt)
```

---

## CLI Design

### ❌ Blocking commands
**Pitfall:** Long-running commands block the terminal.

**Solution:** Use Rich for progress indicators and streaming.

```python
# Bad
result = client.chat(prompt)
print(result)

# Good
with console.status("[bold green]Processing..."):
    for chunk in client.stream_chat(prompt):
        console.print(chunk)
```

### ❌ Poor error messages
**Pitfall:** Generic error messages confuse users.

**Solution:** Provide actionable error messages.

```python
# Bad
raise Exception("Error occurred")

# Good
raise APIError(f"MiniMax API error: {response.status_code}. Check your API key.")
```

---

## Session Tracking

### ❌ Not persisting session state
**Pitfall:** Session data lost on restart.

**Solution:** Persist to file or database.

```python
# Bad
session = Session()  # In-memory only

# Good
session = Session.load_from_file("session.json")
```

---

## VSCode Extension

### ❌ Blocking main thread
**Pitfall:** Long operations freeze VSCode.

**Solution:** Use async/await and worker threads.

```python
# Bad
const result = await longRunningTask();

# Good
await vscode.window.withProgress({ location: ... }, async () => {
    const result = await longRunningTask();
});
```

### ❌ Not handling missing Python
**Pitfall:** Extension fails without Python installed.

**Solution:** Check for Python and provide clear error.

---

## Testing

### ❌ Not mocking API calls
**Pitfall:** Tests make real API calls (expensive).

**Solution:** Mock the API client.

```python
@pytest.fixture
def mock_client(monkeypatch):
    def mock_post(*args, **kwargs):
        return Mock(response={"choices": [...]})
    monkeypatch.setattr(httpx.Client, "post", mock_post)
```

---

## Performance

### ❌ Not batching requests
**Pitfall:** Making many small API calls (expensive).

**Solution:** Combine multiple requests.

```python
# Bad
for item in items:
    client.chat(item)

# Good
batched = batcher.combine(items)
client.chat(batched)
```

### ❌ Not caching token counts
**Pitfall:** Re-counting same prompts repeatedly.

**Solution:** Cache token counts.

```python
cache = {}
def count_tokens(text):
    if text in cache:
        return cache[text]
    count = actual_count(text)
    cache[text] = count
    return count
```

---

*Avoid these pitfalls to build a robust, efficient TokenCUNT.*
