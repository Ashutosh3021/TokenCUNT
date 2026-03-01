# TokenCUNT — Requirements

> Functional and non-functional requirements for the project.

---

## Functional Requirements

### Core Engine

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-01 | API client must connect to MiniMax API | MUST |
| REQ-02 | Token counter must estimate before API calls | MUST |
| REQ-03 | Token counter must track actual usage | MUST |
| REQ-04 | Budget manager must enforce session limits | MUST |
| REQ-05 | Budget manager must alert at 80% threshold | SHOULD |
| REQ-06 | Batcher must combine multiple requests | SHOULD |
| REQ-07 | Optimizer must reduce prompt size | SHOULD |
| REQ-08 | Session must track all operations | MUST |

### CLI Tool

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-09 | CLI must have `ask` command | MUST |
| REQ-10 | CLI must support `--dry-run` flag | MUST |
| REQ-11 | CLI must have `analyze` command | SHOULD |
| REQ-12 | CLI must have `batch` command | SHOULD |
| REQ-13 | CLI must have `report` command | MUST |
| REQ-14 | CLI must have `session` command | SHOULD |
| REQ-15 | CLI must display token costs | MUST |
| REQ-16 | CLI must show budget status | SHOULD |

### VSCode Extension

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-17 | Extension must show status bar | MUST |
| REQ-18 | Status bar must show token usage | MUST |
| REQ-19 | Extension must provide inline hints | SHOULD |
| REQ-20 | Extension must show budget alerts | SHOULD |
| REQ-21 | Extension must have command palette | MUST |
| REQ-22 | Extension must have side panel | COULD |

---

## Non-Functional Requirements

### Performance

| ID | Requirement | Target |
|----|-------------|--------|
| PERF-01 | Token estimation must complete in <100ms | <100ms |
| PERF-02 | CLI commands must respond in <1s (no API) | <1s |
| PERF-03 | VSCode extension must not block UI | 0ms blocking |

### Reliability

| ID | Requirement | Priority |
|----|-------------|----------|
| REL-01 | Must handle API errors gracefully | MUST |
| REL-02 | Must retry on transient failures | MUST |
| REL-03 | Must save session on unexpected exit | SHOULD |

### Usability

| ID | Requirement | Priority |
|----|-------------|----------|
| USE-01 | CLI must have helpful error messages | MUST |
| USE-02 | CLI must show progress for long operations | SHOULD |
| USE-03 | Status bar must be readable | MUST |

---

## Technical Requirements

### Configuration

| ID | Requirement |
|----|-------------|
| CONF-01 | API key must be set via environment variable |
| CONF-02 | Default budget must be configurable |
| CONF-03 | Model selection must be configurable |

### Compatibility

| ID | Requirement |
|----|-------------|
| COMP-01 | Must work with Python 3.10+ |
| COMP-02 | Must work with VSCode 1.75+ |

---

## Feature Matrix

| Feature | Phase 1 | Phase 2 | Phase 3 |
|---------|---------|---------|---------|
| API Client | ✓ | | |
| Token Counter | ✓ | | |
| Budget Manager | ✓ | | |
| Request Batcher | ✓ | | |
| Prompt Optimizer | ✓ | | |
| Session Tracker | ✓ | | |
| Ask Command | | ✓ | |
| Analyze Command | | ✓ | |
| Batch Command | | ✓ | |
| Report Command | | ✓ | |
| Status Bar | | | ✓ |
| Inline Hints | | | ✓ |
| Budget Alerts | | | ✓ |
| Command Palette | | | ✓ |
| Side Panel | | | ✓ |

---

*Requirements defined. Ready for roadmap creation.*
