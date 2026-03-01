# TokenCUNT — Feature Specification

> Detailed feature breakdown for each phase.

---

## Phase 1: Core Engine Features

### 1.1 API Client (`api_client.py`)

| Feature | Description |
|---------|-------------|
| **MiniMax Connection** | HTTP client configured for MiniMax API |
| **Request Builder** | Construct properly formatted API requests |
| **Response Handler** | Parse and validate API responses |
| **Error Handling** | Graceful handling of API errors |
| **Retry Logic** | Automatic retry with exponential backoff |

### 1.2 Token Counter (`token_counter.py`)

| Feature | Description |
|---------|-------------|
| **Pre-call Estimation** | Count tokens before sending (dry run) |
| **Post-call Tracking** | Count actual tokens used |
| **Model-specific** | Handle different tokenization per model |
| **Caching** | Cache token counts for repeated prompts |

### 1.3 Budget Manager (`budget.py`)

| Feature | Description |
|---------|-------------|
| **Budget Setting** | Set token limit per session |
| **Threshold Alerts** | Warning at 80% of budget |
| **Hard Limits** | Block requests exceeding remaining budget |
| **Budget Reset** | Clear or reset budget mid-session |

### 1.4 Smart Batcher (`batcher.py`)

| Feature | Description |
|---------|-------------|
| **Auto-batching** | Combine multiple small requests |
| **Batch Size** | Configurable max batch size |
| **Priority Queue** | Handle urgent requests first |
| **Batch Execution** | Execute batched requests efficiently |

### 1.5 Prompt Optimizer (`optimizer.py`)

| Feature | Description |
|---------|-------------|
| **Context Trimming** | Remove redundant context |
| **Compression** | Compress prompts without losing meaning |
| **Template Optimization** | Use efficient prompt templates |
| **History Management** | Summarize old conversation history |

### 1.6 Session Tracker (`session.py`)

| Feature | Description |
|---------|-------------|
| **Session Lifecycle** | Start, track, and end sessions |
| **Usage Recording** | Record all API calls and token usage |
| **Statistics** | Calculate session statistics |
| **Report Generation** | Generate usage summary reports |

---

## Phase 2: CLI Tool Features

### 2.1 Ask Command

| Feature | Description |
|---------|-------------|
| **Question Prompt** | Send question to AI with context |
| **File Attachment** | Include file contents in prompt |
| **Dry Run Mode** | Preview token cost without sending |
| **Streaming Response** | Stream AI response in real-time |

### 2.2 Analyze Command

| Feature | Description |
|---------|-------------|
| **Code Analysis** | Analyze file and suggest improvements |
| **Issue Detection** | Identify potential problems |
| **Refactoring** | Suggest refactoring options |
| **Token Report** | Show token cost for analysis |

### 2.3 Batch Command

| Feature | Description |
|---------|-------------|
| **Task File** | Read tasks from text file |
| **Progress Tracking** | Show progress for batch jobs |
| **Error Handling** | Continue on individual task failure |
| **Summary Report** | Show results for all tasks |

### 2.4 Report Command

| Feature | Description |
|---------|-------------|
| **Usage Summary** | Show total tokens used |
| **Per-Task Breakdown** | List tokens per operation |
| **Budget Status** | Show current budget usage |
| **Export Options** | Export report as JSON/CSV |

### 2.5 Session Command

| Feature | Description |
|---------|-------------|
| **Budget Configuration** | Set session token budget |
| **Session Info** | Show current session details |
| **Reset Session** | Clear current session |

---

## Phase 3: VSCode Extension Features

### 3.1 Status Bar

| Feature | Description |
|---------|-------------|
| **Live Token Count** | Display current session tokens |
| **Budget Percentage** | Show percentage of budget used |
| **Quick Actions** | Click to access common commands |
| **Color Coding** | Green/Yellow/Red based on usage |

### 3.2 Inline Hints

| Feature | Description |
|---------|-------------|
| **Hover Preview** | Show token cost on hover |
| **Selection Analysis** | Analyze selected code portion |
| **Quick Actions** | Send to AI directly from hint |

### 3.3 Budget Alerts

| Feature | Description |
|---------|-------------|
| **Warning Popup** | Alert at 80% budget |
| **Critical Alert** | Alert at 95% budget |
| **Action Options** | Option to increase budget or clear |

### 3.4 Command Palette

| Feature | Description |
|---------|-------------|
| **Analyze File** | Run analysis on current file |
| **Show Report** | Display session report |
| **Ask Question** | Open input for question |
| **Clear Session** | Reset current session |

### 3.5 Side Panel

| Feature | Description |
|---------|-------------|
| **Usage Breakdown** | Detailed per-task breakdown |
| **History View** | View past sessions |
| **Export Data** | Export session data |

---

*All features designed for token efficiency and developer productivity.*
