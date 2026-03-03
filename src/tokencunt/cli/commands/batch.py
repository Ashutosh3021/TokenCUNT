"""Batch command - Process multiple tasks from JSON."""

import asyncio
import json
from pathlib import Path
from typing import Optional, List, Any

import typer
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_ERROR, EXIT_INVALID_ARGS
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core import (
    MiniMaxApiClient,
    TokenCounter,
    BudgetManager,
    BudgetConfig,
    RequestBatcher,
)
from tokencunt.config import config


async def _execute_batch(
    tasks: List[dict],
    output_file: Optional[Path],
    formatter: OutputFormatter,
) -> int:
    """Execute batch tasks."""
    if not config.is_configured:
        formatter.error(
            "API not configured",
            suggestion="Set MINIMAX_API_KEY and MINIMAX_GROUP_ID environment variables",
        )
        return EXIT_ERROR

    try:
        budget_config = BudgetConfig(max_tokens=config.default_budget)
        budget_manager = BudgetManager(budget_config)
        token_counter = TokenCounter()
    except Exception as e:
        formatter.error(f"Failed to initialize: {e}")
        return EXIT_ERROR

    results: List[dict] = []

    try:
        client = MiniMaxApiClient(
            api_key=config.api_key,
            group_id=config.group_id,
            model=config.default_model,
        )

        for i, task in enumerate(tasks):
            prompt = task.get("prompt", "")
            if not prompt:
                continue

            estimated = token_counter.count(prompt)

            # Check budget
            status, warning = budget_manager.check_budget(estimated)
            if status.value == "exceeded":
                formatter.warning(f"Task {i + 1}: Budget exceeded, skipping")
                continue
            if warning:
                formatter.warning(f"Task {i + 1}: {warning}")

            try:
                response = await client.chat(
                    messages=[{"role": "user", "content": prompt}],
                )

                result = {
                    "task_index": i,
                    "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "response": response.content,
                    "usage": response.usage.__dict__ if response.usage else None,
                }

                if response.usage:
                    budget_manager.add_usage(response.usage.total_tokens)

                results.append(result)

            except Exception as e:
                formatter.warning(f"Task {i + 1} failed: {e}")
                results.append(
                    {
                        "task_index": i,
                        "error": str(e),
                    }
                )

        await client.close()

        # Save results
        if output_file:
            output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
            formatter.success(f"Results saved to {output_file}")
        else:
            for result in results:
                if "error" in result:
                    formatter.error(
                        f"Task {result['task_index'] + 1}: {result['error']}"
                    )
                else:
                    formatter.print_response(result.get("response", ""))

        formatter.print_table(
            formatter.format_budget_status(
                budget_manager.current_usage,
                budget_config.max_tokens,
            )
        )

        formatter.success(f"Batch complete: {len(results)} tasks processed")
        return EXIT_SUCCESS

    except Exception as e:
        formatter.error(f"Batch execution failed: {e}")
        if formatter.debug:
            formatter.debug_info({"error": str(e)})
        return EXIT_ERROR


@app.command(name="batch")
def batch_command(
    file: Annotated[Path, typer.Argument(help="JSON file with tasks")],
    output: Annotated[
        Optional[Path],
        typer.Option("-o", "--output", help="Output file for results"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run/--no-dry-run", help="Show estimate without executing"),
    ] = True,
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Process multiple tasks from a JSON file.

    Input JSON format:
    {
        "tasks": [
            {"prompt": "Task 1 description"},
            {"prompt": "Task 2 description"}
        ]
    }

    Use --dry-run (default) to see total estimate without executing.
    Use --output to save results to a file.
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

    # Read JSON file
    if not file.exists():
        formatter.error(f"File not found: {file}")
        return EXIT_INVALID_ARGS

    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        tasks = data.get("tasks", [])
    except json.JSONDecodeError as e:
        formatter.error(f"Invalid JSON: {e}")
        return EXIT_INVALID_ARGS
    except Exception as e:
        formatter.error(f"Failed to read file: {e}")
        return EXIT_INVALID_ARGS

    if not tasks:
        formatter.warning("No tasks found in file")
        return EXIT_SUCCESS

    # Initialize for estimation
    try:
        budget_config = BudgetConfig(max_tokens=config.default_budget)
        budget_manager = BudgetManager(budget_config)
        token_counter = TokenCounter()
    except Exception as e:
        formatter.error(f"Failed to initialize: {e}")
        return EXIT_ERROR

    # Estimate total tokens
    total_estimate = 0
    for task in tasks:
        prompt = task.get("prompt", "")
        if prompt:
            total_estimate += token_counter.count(prompt)

    # Show estimate in dry-run mode
    if dry_run:
        if not quiet:
            formatter.info(f"Total tasks: {len(tasks)}")
            formatter.info(f"Total token estimate: {total_estimate:,} tokens")
            formatter.print_table(formatter.format_token_cost(total_estimate))

            formatter.info("Budget status:")
            formatter.print_table(
                formatter.format_budget_status(
                    budget_manager.current_usage,
                    budget_config.max_tokens,
                )
            )

            formatter.warning(
                "Dry-run mode: No tasks executed. Use --no-dry-run to run."
            )
        return EXIT_SUCCESS

    # Execute batch
    return asyncio.run(_execute_batch(tasks, output, formatter))
