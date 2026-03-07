"""Optimize command - AI + rule-based prompt optimization."""

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_INVALID_ARGS
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core.prompt_optimizer import PromptOptimizer


@app.command(name="optimize")
def optimize_command(
    prompt_source: Annotated[
        Optional[str],
        typer.Argument(help="Prompt file path or inline prompt text"),
    ] = None,
    rules_only: Annotated[
        bool,
        typer.Option("--rules-only", help="Use rule-based optimization only"),
    ] = False,
    ai_only: Annotated[
        bool,
        typer.Option("--ai-only", help="Use AI optimization only (requires API key)"),
    ] = False,
    hybrid: Annotated[
        bool,
        typer.Option("--hybrid", help="Use both AI and rules (default)"),
    ] = False,
    model: Annotated[
        str,
        typer.Option("--model", "-m", help="Model to use for AI optimization"),
    ] = "MiniMax-Text-01",
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Save optimized prompt to file"),
    ] = None,
    show_diff: Annotated[
        bool,
        typer.Option("--show-diff", help="Show diff of changes made"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output results as JSON"),
    ] = False,
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Optimize prompts using AI and/or rule-based techniques.

    Examples:

        Optimize a prompt file with rules only:
        $ ts optimize prompt.txt --rules-only

        Optimize with AI (requires API key):
        $ ts optimize prompt.txt --ai-only

        Use hybrid mode (default):
        $ ts optimize prompt.txt

        Optimize inline text:
        $ ts optimize "Please help me with this task"

        Save optimized version:
        $ ts optimize prompt.txt -o optimized.txt
    """
    console = Console()

    # Determine mode
    if rules_only:
        mode = "rules"
    elif ai_only:
        mode = "ai"
    else:
        mode = "hybrid"

    # Get prompt text
    if prompt_source is None:
        console.print("[red]Error:[/red] Please provide a prompt file or text")
        return EXIT_INVALID_ARGS

    # Check if it's a file path or inline text
    prompt_path = Path(prompt_source) if prompt_source else None
    if prompt_path and prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            original_prompt = f.read()
    else:
        # Treat as inline text
        original_prompt = prompt_source

    if not original_prompt.strip():
        console.print("[red]Error:[/red] Prompt is empty")
        return EXIT_INVALID_ARGS

    # Get API key if needed
    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("OPENAI_API_KEY")

    if mode in ("ai", "hybrid") and not api_key:
        console.print(
            "[yellow]Warning:[/yellow] No API key found. "
            "Falling back to rules-only mode."
        )
        mode = "rules"

    # Create optimizer
    optimizer = PromptOptimizer(api_key=api_key, model=model)

    # Run optimization
    try:
        if mode == "rules":
            result = optimizer.optimize_with_rules(original_prompt)
        elif mode == "ai":
            result = optimizer.optimize_with_ai(original_prompt)
        else:
            result = optimizer.optimize_hybrid(original_prompt)
    except Exception as e:
        console.print(f"[red]Error during optimization:[/red] {str(e)}")
        return EXIT_INVALID_ARGS

    # Output results
    if json_output:
        import json

        output_data = {
            "original": result.original_prompt,
            "optimized": result.optimized_prompt,
            "original_tokens": result.original_tokens,
            "optimized_tokens": result.optimized_tokens,
            "tokens_saved": result.original_tokens - result.optimized_tokens,
            "percent_saved": (
                (result.original_tokens - result.optimized_tokens) / result.original_tokens * 100
                if result.original_tokens > 0
                else 0
            ),
            "mode": result.mode,
            "suggestions": [
                {
                    "rule": s.rule_name,
                    "tokens_saved": s.tokens_saved,
                }
                for s in result.suggestions
            ],
        }
        console.print(json.dumps(output_data, indent=2))
        return EXIT_SUCCESS

    # Rich formatted output
    tokens_saved = result.original_tokens - result.optimized_tokens
    percent_saved = (
        tokens_saved / result.original_tokens * 100 if result.original_tokens > 0 else 0
    )

    # Calculate cost savings (rough estimate)
    cost_per_1k = 0.03  # GPT-4 pricing
    cost_saved = (tokens_saved / 1000) * cost_per_1k

    # Title panel
    title = f"[bold cyan]PROMPT OPTIMIZER ({mode.upper()})[/bold cyan]"
    console.print(Panel("", title=title, border_style="cyan"))

    # Original prompt
    console.print(f"\n[bold]ORIGINAL ({result.original_tokens} tokens):[/bold]")
    console.print(f"[dim]{result.original_prompt[:200]}{'...' if len(result.original_prompt) > 200 else ''}[/dim]")

    console.print("\n" + "-" * 60)

    # Optimized prompt
    console.print(f"\n[bold]OPTIMIZED ({result.optimized_tokens} tokens):[/bold]")
    console.print(f"[green]{result.optimized_prompt[:200]}{'...' if len(result.optimized_prompt) > 200 else ''}[/green]")

    console.print("\n" + "-" * 60)

    # Reduction stats
    console.print(f"\n[bold cyan]REDUCTION:[/bold cyan] {tokens_saved} tokens ({percent_saved:.1f}%)")
    console.print(f"[bold cyan]ESTIMATED SAVINGS:[/bold cyan] ${cost_saved:.4f}/run")

    # Suggestions
    if result.suggestions:
        console.print("\n" + "-" * 60)
        console.print("\n[bold]SUGGESTIONS:[/bold]")

        table = Table(show_header=False, box=None)
        table.add_column("checkbox", style="green")
        table.add_column("rule", style="white")
        table.add_column("savings", style="dim")

        for suggestion in result.suggestions:
            table.add_row(
                "[*]",
                suggestion.rule_name,
                f"(-{suggestion.tokens_saved} tokens)",
            )

        console.print(table)

    # Show diff if requested
    if show_diff and result.original_prompt != result.optimized_prompt:
        console.print("\n" + "-" * 60)
        console.print("\n[bold]DIFF:[/bold]")
        
        # Simple line-by-line diff visualization
        original_lines = result.original_prompt.split('\n')
        optimized_lines = result.optimized_prompt.split('\n')
        
        # Show side-by-side comparison
        from rich.columns import Columns
        from rich.text import Text
        
        for i, (orig_line, opt_line) in enumerate(zip(original_lines, optimized_lines), 1):
            if orig_line != opt_line:
                console.print(f"[red]-{i}: {orig_line}[/red]")
                console.print(f"[green]+{i}: {opt_line}[/green]")
        
        # Handle lines that only exist in one version
        if len(original_lines) > len(optimized_lines):
            for i in range(len(optimized_lines), len(original_lines) + 1):
                console.print(f"[red]-{i}: {original_lines[i-1]}[/red]")
        elif len(optimized_lines) > len(original_lines):
            for i in range(len(original_lines), len(optimized_lines) + 1):
                console.print(f"[green]+{i}: {optimized_lines[i-1]}[/green]")

    console.print("\n" + "-" * 60 + "\n")

    # Save to file if requested
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result.optimized_prompt)
        console.print(f"[green]Optimized prompt saved to:[/green] {output}")

    return EXIT_SUCCESS


if __name__ == "__main__":
    optimize_command()
