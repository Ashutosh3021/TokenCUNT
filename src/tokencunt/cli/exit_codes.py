"""Exit code constants for CLI."""

# Success
EXIT_SUCCESS = 0

# Errors
EXIT_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_BUDGET_EXCEEDED = 3

# Signals
EXIT_INTERRUPT = 130  # Standard for SIGINT (Ctrl+C)

__all__ = [
    "EXIT_SUCCESS",
    "EXIT_ERROR",
    "EXIT_INVALID_ARGS",
    "EXIT_BUDGET_EXCEEDED",
    "EXIT_INTERRUPT",
]
