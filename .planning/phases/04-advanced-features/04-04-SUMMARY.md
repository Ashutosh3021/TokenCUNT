# Plan 04-04: Prompt Optimizer - Summary

**Plan:** 04-04
**Phase:** 04-advanced-features
**Status:** Complete

---

## Tasks Completed

### Task 1: Create prompt optimizer module
- Created `src/tokencunt/core/prompt_optimizer.py`
- Implemented `PromptOptimizer` class with:
  - `optimize_with_rules()` - Rule-based optimization
  - `optimize_with_ai()` - AI optimization (placeholder)
  - `optimize_hybrid()` - Combined approach
  - `get_suggestions()` - List possible optimizations

### Task 2: Create ts optimize CLI command
- Created `src/tokencunt/cli/commands/optimize.py`
- Implemented `ts optimize` command with:
  - File argument or inline text
  - `--rules-only`: Rule-based only
  - `--ai-only`: AI only
  - `--hybrid`: Both (default)
  - `--model`: Model selection
  - `--output`, `-o`: Save to file
  - `--show-diff`: Show diff of changes made
  - `--json`: JSON output

### Task 3: Wire optimize command to CLI
- Added optimize to `commands/__init__.py`
- Command registered and functional

---

## Verification Results

- `python -c "from tokencunt.core.prompt_optimizer import PromptOptimizer; print('Optimizer imported')"` - PASS
- `python -c "from tokencunt.cli.commands.optimize import optimize_command; print('Optimize command loads')"` - PASS
- `ts optimize --help` - PASS
- `ts optimize --show-diff` - PASS
- JSON output - PASS

---

## Files Modified

- `src/tokencunt/core/prompt_optimizer.py` (new)
- `src/tokencunt/cli/commands/optimize.py` (new)
- `src/tokencunt/cli/commands/__init__.py` (modified)

---

## Test Output

```
$ ts optimize "Please help me with this task please" --rules-only

+------------------------- PROMPT OPTIMIZER (RULES) --------------------------+

ORIGINAL (7 tokens):
Please help me with this task please

------------------------------------------------------------

OPTIMIZED (5 tokens):
help me with this task

------------------------------------------------------------

REDUCTION: 2 tokens (28.6%)
ESTIMATED SAVINGS: $0.0001/run

------------------------------------------------------------

SUGGESTIONS:
 [*]  Remove '\bplease\b'  (-1 tokens) 

------------------------------------------------------------
```

### Test with --show-diff

```
$ ts optimize "Please help the user with their questions..." --rules-only --show-diff

...

DIFF:
-1: Please help the user with their questions...
+1: assist user with their questions...

------------------------------------------------------------
```

---

## Notes

- Rule-based optimizations remove filler words (please, kindly) and simplify phrases
- AI optimization requires API key (falls back to rules-only if not available)
- Hybrid mode combines both approaches
- Windows console encoding handled with ASCII-safe characters
- Used ASCII arrows (->) instead of Unicode (→) for Windows compatibility
