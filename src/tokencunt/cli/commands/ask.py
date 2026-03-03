"""Ask command - Ask questions with token tracking."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_ERROR, EXIT_INVALID_ARGS
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core import MiniMaxApiClient, TokenCounter, BudgetManager, BudgetConfig
from tokencunt.config import config


async def _execute_ask(
    prompt: str,
    model: Optional[str],
    formatter: OutputFormatter,
) -> int:
    """Execute the actual API call."""
    # Check API credentials
    if not config.is_configured:
        formatter.error(
            "API not configured",
            suggestion="Set MINIMAX_API_KEY and MINIMAX_GROUP_ID environment variables",
        )
        return EXIT_ERROR

    # Initialize components
    try:
        budget_config = BudgetConfig(max_tokens=config.default_budget)
        budget_manager = BudgetManager(budget_config)
        token_counter = TokenCounter()
    except Exception as e:
        formatter.error(f"Failed to initialize: {e}")
        return EXIT_ERROR

    # Estimate tokens
    estimated_tokens = token_counter.count(prompt)

    # Check budget
    status, warning = budget_manager.check_budget(estimated_tokens)
    if status.value == "exceeded":
        formatter.error("Budget exceeded")
        return EXIT_ERROR
    if warning:
        formatter.warning(warning)

    # Execute API call
    try:
        client = MiniMaxApiClient(
            api_key=config.api_key,
            group_id=config.group_id,
            model=model or config.default_model,
        )
        response = await client.chat(
            messages=[{"role": "user", "content": prompt}],
        )

        # Display response
        if response.usage:
            formatter.print_table(
                formatter.format_token_cost(
                    estimated_tokens,
                    response.usage.completion_tokens + response.usage.prompt_tokens,
                )
            )

        formatter.print_response(response.content)

        # Update budget
        if response.usage:
            budget_manager.add_usage(response.usage.total_tokens)

            formatter.print_table(
                formatter.format_budget_status(
                    budget_manager.current_usage,
                    budget_config.max_tokens,
                )
            )

        formatter.success("Request completed")

        # Debug info
        if formatter.debug:
            formatter.debug_info(
                {
                    "model": response.model,
                    "usage": response.usage.__dict__ if response.usage else None,
                }
            )

        await client.close()
        return EXIT_SUCCESS

    except Exception as e:
        formatter.error(f"API call failed: {e}")
        if formatter.debug:
            formatter.debug_info({"error": str(e)})
        return EXIT_ERROR


@app.command(name="ask")
def ask_command(
    prompt: Annotated[str, typer.Argument(help="The prompt to send")],
    file: Annotated[
        Optional[Path], typer.Option("-f", "--file", help="File containing prompt")
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run/--no-dry-run", help="Show estimate without calling API"
        ),
    ] = True,
    model: Annotated[
        Optional[str], typer.Option("--model", help="Model to use")
    ] = None,
    # Global options via typer.Context
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Ask a question with token tracking.

    If --file is provided, reads content from file as prompt.
    Use --dry-run (default) to see token estimate without API call.
    """
    # Get global options from context
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

    # Get prompt from file if provided
    if file:
        if not file.exists():
            formatter.error(f"File not found: {file}")
            return EXIT_INVALID_ARGS
        try:
            prompt = file.read_text(encoding="utf-8")
        except Exception as e:
            formatter.error(f"Failed to read file: {e}")
            return EXIT_INVALID_ARGS

    # Initialize components for estimation
    try:
        budget_config = BudgetConfig(max_tokens=config.default_budget)
        budget_manager = BudgetManager(budget_config)
        token_counter = TokenCounter()
    except Exception as e:
        formatter.error(f"Failed to initialize: {e}")
        if debug:
            formatter.debug_info({"error": str(e)})
        return EXIT_ERROR

    # Estimate tokens
    estimated_tokens = token_counter.count(prompt)

    # Show estimate in dry-run mode
    if dry_run:
        if not quiet:
            formatter.info(f"Token estimate: {estimated_tokens:,} tokens")
            formatter.print_table(formatter.format_token_cost(estimated_tokens))

            formatter.info("Budget status:")
            formatter.print_table(
                formatter.format_budget_status(
                    budget_manager.current_usage,
                    budget_config.max_tokens,
                )
            )

            formatter.warning(
                "Dry-run mode: No API call made. Use --no-dry-run to execute."
            )
        return EXIT_SUCCESS

    # Execute API call (async)
    return asyncio.run(_execute_ask(prompt, model, formatter))
