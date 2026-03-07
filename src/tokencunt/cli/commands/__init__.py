"""CLI commands package."""

# Import all commands to register them with the app
from tokencunt.cli.commands import (
    ask,
    analyze,
    batch,
    report,
    session,
    scan,
    simulate,
    diff,
    optimize,
)

__all__ = ["ask", "analyze", "batch", "report", "session", "scan", "simulate", "diff", "optimize"]
