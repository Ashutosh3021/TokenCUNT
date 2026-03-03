"""Analyze command - Analyze files for improvements."""

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


ANALYSIS_SYSTEM_PROMPT = """You are a code analysis expert. Analyze the provided code and identify:
1. Potential bugs or issues
2. Performance improvements
3. Code style and best practices
4. Security concerns
5. Suggestions for refactoring

Provide your analysis in a clear, structured format.
"""


async def _execute_analyze(
    file: Path,
    prompt: str,
    model: Optional[str],
    formatter: OutputFormatter,
) -> int:
    """Execute the actual analysis API call."""
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

    estimated_tokens = token_counter.count(prompt)

    status, warning = budget_manager.check_budget(estimated_tokens)
    if status.value == "exceeded":
        formatter.error("Budget exceeded")
        return EXIT_ERROR
    if warning:
        formatter.warning(warning)

    try:
        client = MiniMaxApiClient(
            api_key=config.api_key,
            group_id=config.group_id,
            model=model or config.default_model,
        )
        response = await client.chat(
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        if response.usage:
            formatter.print_table(
                formatter.format_token_cost(
                    estimated_tokens,
                    response.usage.completion_tokens + response.usage.prompt_tokens,
                )
            )

        formatter.print_response(response.content, format="markdown")

        if response.usage:
            budget_manager.add_usage(response.usage.total_tokens)
            formatter.print_table(
                formatter.format_budget_status(
                    budget_manager.current_usage,
                    budget_config.max_tokens,
                )
            )

        formatter.success(f"Analysis complete for {file.name}")

        if formatter.debug:
            formatter.debug_info(
                {
                    "file": str(file),
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


@app.command(name="analyze")
def analyze_command(
    file: Annotated[Path, typer.Argument(help="File to analyze")],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run/--no-dry-run", help="Show estimate without calling API"
        ),
    ] = True,
    focus: Annotated[
        Optional[str],
        typer.Option("--focus", help="Focus area: bugs, performance, style, security"),
    ] = None,
    model: Annotated[
        Optional[str], typer.Option("--model", help="Model to use")
    ] = None,
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Analyze a file for improvements.

    Reads the file content and sends it for AI analysis.
    Use --focus to specify what to analyze (bugs, performance, style).
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

    # Read file content
    if not file.exists():
        formatter.error(f"File not found: {file}")
        return EXIT_INVALID_ARGS

    try:
        content = file.read_text(encoding="utf-8")
    except Exception as e:
        formatter.error(f"Failed to read file: {e}")
        return EXIT_INVALID_ARGS

    # Build analysis prompt
    focus_instruction = ""
    if focus:
        focus_instruction = f"\nFocus specifically on: {focus}. "

    analysis_prompt = f"""Please analyze the following code:

```{file.suffix.lstrip(".")}
{content}
```

{focus_instruction}Provide specific, actionable suggestions.
"""

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
    estimated_tokens = token_counter.count(analysis_prompt)

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

    # Execute API call
    return asyncio.run(_execute_analyze(file, analysis_prompt, model, formatter))
