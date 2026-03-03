"""Session command - Manage session settings."""

import json
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_ERROR
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core import SessionManager, Session
from tokencunt.core.budget import BudgetConfig
from tokencunt.config import config


@app.command(name="session")
def session_command(
    action: Annotated[
        str,
        typer.Argument(help="Action: new, list, show, config, clear"),
    ] = "show",
    budget: Annotated[
        Optional[int],
        typer.Option("--budget", help="Set budget limit (tokens)"),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", help="Set default model"),
    ] = None,
    session_id: Annotated[
        Optional[str],
        typer.Option("--session", help="Session ID for show/clear actions"),
    ] = None,
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Manage sessions.

    Actions:
    - new: Create a new session
    - list: List all sessions
    - show: Show current/last session details
    - config: Configure budget/model for current session
    - clear: Clear session data
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

    try:
        session_manager = SessionManager()
    except Exception as e:
        formatter.error(f"Failed to initialize session manager: {e}")
        return EXIT_ERROR

    action = action.lower()

    if action == "new":
        try:
            new_session = session_manager.create_session()
            formatter.success(f"Created new session: {new_session.session_id}")
            return EXIT_SUCCESS
        except Exception as e:
            formatter.error(f"Failed to create session: {e}")
            return EXIT_ERROR

    elif action == "list":
        try:
            session_ids = session_manager.list_sessions()

            if json_output:
                data = []
                for sid in session_ids:
                    sess = session_manager.load_session(sid)
                    if sess:
                        data.append(
                            {
                                "id": sid,
                                "created_at": sess.created_at.isoformat()
                                if sess.created_at
                                else None,
                                "request_count": len(sess.requests),
                            }
                        )
                formatter.console.print_json(json.dumps(data, default=str))
                return EXIT_SUCCESS

            from rich.table import Table

            table = Table(title="Sessions")
            table.add_column("ID", style="cyan")
            table.add_column("Created", style="dim")
            table.add_column("Requests", justify="right")

            for sid in session_ids:
                sess = session_manager.load_session(sid)
                if sess:
                    ts = (
                        sess.created_at.strftime("%Y-%m-%d %H:%M")
                        if sess.created_at
                        else "Unknown"
                    )
                    table.add_row(sid[:8], ts, str(len(sess.requests)))

            formatter.print_table(table)
            formatter.success(f"Total: {len(session_ids)} sessions")
            return EXIT_SUCCESS

        except Exception as e:
            formatter.error(f"Failed to list sessions: {e}")
            return EXIT_ERROR

    elif action == "show":
        try:
            session_ids = session_manager.list_sessions()

            if not session_ids:
                formatter.warning("No sessions found")
                return EXIT_SUCCESS

            target = None
            if session_id:
                target = session_manager.load_session(session_id)
                if not target:
                    formatter.error(f"Session not found: {session_id}")
                    return EXIT_ERROR
            else:
                # Get most recent session
                if session_ids:
                    target = session_manager.load_session(session_ids[0])

            if not target:
                formatter.error("Failed to load session")
                return EXIT_ERROR

            if json_output:
                data = {
                    "id": target.session_id,
                    "created_at": target.created_at.isoformat()
                    if target.created_at
                    else None,
                    "requests": [
                        {
                            "timestamp": r.timestamp.isoformat()
                            if r.timestamp
                            else None,
                            "input_tokens": r.input_tokens,
                            "output_tokens": r.output_tokens,
                        }
                        for r in target.requests
                    ],
                }
                formatter.console.print_json(json.dumps(data, default=str))
                return EXIT_SUCCESS

            from rich.table import Table

            table = Table(title=f"Session: {target.session_id}", show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("ID", target.session_id)
            table.add_row(
                "Created",
                target.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if target.created_at
                else "Unknown",
            )
            table.add_row("Requests", str(len(target.requests)))

            formatter.print_table(table)
            formatter.success("Session details shown")
            return EXIT_SUCCESS

        except Exception as e:
            formatter.error(f"Failed to show session: {e}")
            return EXIT_ERROR

    elif action == "config":
        try:
            # Read current config
            current_budget = config.default_budget
            current_model = config.default_model

            if budget is not None:
                config.default_budget = budget
                formatter.success(f"Set budget to {budget:,} tokens")
            else:
                formatter.info(f"Current budget: {current_budget:,} tokens")

            if model is not None:
                config.default_model = model
                formatter.success(f"Set model to {model}")
            else:
                formatter.info(f"Current model: {current_model}")

            formatter.success("Configuration updated")
            return EXIT_SUCCESS

        except Exception as e:
            formatter.error(f"Failed to update config: {e}")
            return EXIT_ERROR

    elif action == "clear":
        try:
            if session_id:
                # Clear specific session
                target = session_manager.load_session(session_id)

                if not target:
                    formatter.error(f"Session not found: {session_id}")
                    return EXIT_ERROR

                success = session_manager.delete_session(session_id)
                if success:
                    formatter.success(f"Deleted session: {session_id}")
                    return EXIT_SUCCESS
                else:
                    formatter.error(f"Failed to delete session: {session_id}")
                    return EXIT_ERROR
            else:
                formatter.warning("Use --session to specify which session to clear")
                return EXIT_ERROR

        except Exception as e:
            formatter.error(f"Failed to clear session: {e}")
            return EXIT_ERROR

    else:
        formatter.error(f"Unknown action: {action}")
        formatter.info("Valid actions: new, list, show, config, clear")
        return EXIT_ERROR
