"""Diff command - Git-style diff for prompt changes."""

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_INVALID_ARGS
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core.differ import PromptDiffer


@app.command(name="diff")
def diff_command(
    original: Annotated[
        Path,
        typer.Argument(..., help="Original prompt file"),
    ],
    optimized: Annotated[
        Path,
        typer.Argument(..., help="Optimized prompt file"),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output results as JSON"),
    ] = False,
    stats_only: Annotated[
        bool,
        typer.Option("--stats", help="Show only statistics, no diff"),
    ] = False,
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Compare two prompt files and show differences.

    Displays a Git-style unified diff between original and optimized prompts,
    along with token count comparison and cost savings.

    Examples:

        Compare two prompt files:
        $ ts diff original.txt optimized.txt

        Show only statistics:
        $ ts diff original.txt optimized.txt --stats

        Output as JSON:
        $ ts diff original.txt optimized.txt --json
    """
    # Get global options from context
    state = ctx.obj if ctx.obj else None
    quiet = state.quiet if state else False
    json_output = json_output or (state.json_output if state else False)
    debug = state.debug if state else False

    formatter = OutputFormatter(
        quiet=quiet,
        verbose=False,
        json_output=json_output,
        debug=debug,
    )

    # Initialize differ
    differ = PromptDiffer()

    # Load files
    try:
        original_text = differ.load_file(original)
    except FileNotFoundError as e:
        formatter.error(f"Original file not found: {original}")
        return EXIT_INVALID_ARGS
    except IOError as e:
        formatter.error(f"Error reading original file: {e}")
        return EXIT_INVALID_ARGS

    try:
        optimized_text = differ.load_file(optimized)
    except FileNotFoundError as e:
        formatter.error(f"Optimized file not found: {optimized}")
        return EXIT_INVALID_ARGS
    except IOError as e:
        formatter.error(f"Error reading optimized file: {e}")
        return EXIT_INVALID_ARGS

    # Compute diff
    result = differ.diff(
        original_text,
        optimized_text,
        original_name=str(original),
        optimized_name=str(optimized),
        include_stats=True,
    )

    # Output based on flags
    if json_output:
        return _output_json(formatter, result, original, optimized)
    elif stats_only:
        return _output_stats_only(formatter, result)
    else:
        return _output_full_diff(formatter, result)


def _output_json(
    formatter: OutputFormatter,
    result: dict,
    original: Path,
    optimized: Path,
) -> int:
    """Output results as JSON."""
    import json

    stats = result.get("stats")

    output = {
        "original_file": str(original),
        "optimized_file": str(optimized),
        "original_tokens": stats.original_tokens,
        "optimized_tokens": stats.optimized_tokens,
        "tokens_saved": stats.tokens_saved,
        "percent_saved": stats.percent_saved,
        "original_cost": stats.original_cost,
        "optimized_cost": stats.optimized_cost,
        "cost_saved": stats.cost_saved,
    }

    formatter.console.print(json.dumps(output, indent=2))
    return EXIT_SUCCESS


def _output_stats_only(formatter: OutputFormatter, result: dict) -> int:
    """Output only statistics."""
    from rich.panel import Panel
    from rich.text import Text

    stats = result.get("stats")
    stats_formatted = result.get("stats_formatted", "")

    formatter.console.print(
        Panel(
            stats_formatted,
            title="[bold cyan]Prompt Statistics[/bold cyan]",
            border_style="cyan",
        )
    )

    return EXIT_SUCCESS


def _output_full_diff(formatter: OutputFormatter, result: dict) -> int:
    """Output full diff with statistics."""
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text

    # Output the diff
    diff_text = result.get("diff", "")

    if diff_text:
        # Use Syntax for colored diff output
        syntax = Syntax(
            diff_text,
            "diff",
            theme="monokai",
            line_numbers=False,
        )
        formatter.console.print(syntax)
    else:
        formatter.console.print("[dim]No differences found[/dim]")

    # Output statistics
    stats_formatted = result.get("stats_formatted", "")

    if stats_formatted:
        formatter.console.print("")
        formatter.console.print(
            Panel(
                stats_formatted,
                title="[bold cyan]Statistics[/bold cyan]",
                border_style="cyan",
            )
        )

    return EXIT_SUCCESS
