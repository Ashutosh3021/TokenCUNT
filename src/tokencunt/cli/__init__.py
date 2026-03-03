"""TokenCUNT CLI package."""

from tokencunt.cli.app import app
from tokencunt.cli.exit_codes import (
    EXIT_SUCCESS,
    EXIT_ERROR,
    EXIT_INVALID_ARGS,
    EXIT_BUDGET_EXCEEDED,
    EXIT_INTERRUPT,
)

# Import commands to register them (uses @app.command decorators)
# Must be after app is imported to avoid circular import issues
from tokencunt.cli import commands  # noqa: F401

__all__ = [
    "app",
    "EXIT_SUCCESS",
    "EXIT_ERROR",
    "EXIT_INVALID_ARGS",
    "EXIT_BUDGET_EXCEEDED",
    "EXIT_INTERRUPT",
]
