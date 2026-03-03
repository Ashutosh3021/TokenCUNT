"""Report command - Show session usage report."""

import json
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_ERROR
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core import SessionManager, RequestRecord
from tokencunt.config import config


@app.command(name="report")
def report_command(
    session: Annotated[
        Optional[str],
        typer.Option("--session", help="Session ID (default: latest)"),
    ] = None,
    format: Annotated[
        Optional[str],
        typer.Option("--format", help="Output format: table, json"),
    ] = "table",
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Show session usage report.

    Displays total requests, token usage, and cost breakdown.
    Use --session to view a specific session.
    Use --format json for machine-readable output.
    """
    # Get global options
    state = ctx.obj if ctx.obj else None
    quiet = state.quiet if state else False
    verbose = state.verbose if state else False
    json_output = state.json_output if state else False
    debug = state.debug if state else False

    formatter = OutputFormatter(
        quiet=quiet,
        verbose=verbose,
        json_output=json_output,
        debug=debug,
    )

    # Determine output format
    output_format = format or ("json" if json_output else "table")

    # Load session
    try:
        session_manager = SessionManager()
    except Exception as e:
        formatter.error(f"Failed to initialize session manager: {e}")
        if debug:
            formatter.debug_info({"error": str(e)})
        return EXIT_ERROR

    try:
        if session:
            target_session = session_manager.load_session(session)

            if not target_session:
                formatter.error(f"Session not found: {session}")
                return EXIT_ERROR
        else:
            # Get latest session
            sessions = session_manager.list_sessions()
            if not sessions:
                formatter.warning("No sessions found")
                return EXIT_SUCCESS
            target_session = session_manager.load_session(sessions[0])

    except Exception as e:
        formatter.error(f"Failed to load session: {e}")
        if debug:
            formatter.debug_info({"error": str(e)})
        return EXIT_ERROR

    # Gather statistics
    requests = target_session.requests
    total_requests = len(requests)

    total_input_tokens = sum(r.input_tokens for r in requests)
    total_output_tokens = sum(r.output_tokens for r in requests)
    total_tokens = total_input_tokens + total_output_tokens

    # Calculate cost (example rates)
    input_cost = total_input_tokens * 0.0001  # $0.10 per 1K tokens
    output_cost = total_output_tokens * 0.0001
    total_cost = input_cost + output_cost

    # Prepare output
    if output_format == "json" or json_output:
        report_data = {
            "session_id": target_session.session_id,
            "created_at": target_session.created_at.isoformat()
            if target_session.created_at
            else None,
            "total_requests": total_requests,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "cost": {
                "input": input_cost,
                "output": output_cost,
                "total": total_cost,
            },
            "requests": [
                {
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                }
                for r in requests
            ],
        }
        formatter.console.print_json(json.dumps(report_data, default=str))
        return EXIT_SUCCESS

    # Table format
    from rich.table import Table

    summary_table = Table(
        title=f"Session: {target_session.session_id[:8]}...", show_header=False
    )
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")

    summary_table.add_row("Total Requests", str(total_requests))
    summary_table.add_row("Input Tokens", f"{total_input_tokens:,}")
    summary_table.add_row("Output Tokens", f"{total_output_tokens:,}")
    summary_table.add_row("Total Tokens", f"{total_tokens:,}")
    summary_table.add_row("Est. Cost", f"${total_cost:.4f}")

    formatter.print_table(summary_table)

    # Show recent requests
    if requests and not quiet:
        from rich.table import Table

        requests_table = Table(title="Recent Requests")
        requests_table.add_column("Time", style="dim")
        requests_table.add_column("Input", justify="right")
        requests_table.add_column("Output", justify="right")
        requests_table.add_column("Total", justify="right")

        for r in requests[-10:]:  # Last 10
            ts = r.timestamp.strftime("%H:%M:%S") if r.timestamp else "--:--:--"
            requests_table.add_row(
                ts,
                f"{r.input_tokens:,}",
                f"{r.output_tokens:,}",
                f"{r.input_tokens + r.output_tokens:,}",
            )

        formatter.print_table(requests_table)

    formatter.success("Report generated")
    return EXIT_SUCCESS
