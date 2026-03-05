"""Scan command for CLI - scan repository for token estimation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from tokencunt.cli.app import app, CLIState
from tokencunt.core.scanner import RepoScanner


console = Console()


@app.command(name="scan")
def scan_command(
    path: Optional[Path] = typer.Argument(
        None,
        help="Directory to scan (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    extensions: Optional[str] = typer.Option(
        None,
        "--extensions",
        "-e",
        help="Comma-separated list of file extensions to include (e.g., py,js,ts)",
    ),
    ignore_file: Optional[Path] = typer.Option(
        None,
        "--ignore",
        "-i",
        help="Path to .tokencuntignore file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show per-file breakdown",
    ),
) -> None:
    """
    Scan a directory for token estimation.

    Scans the specified directory (or current directory) and estimates
    token counts for all supported files. Respects .tokencuntignore files.
    """
    # Default to current directory
    if path is None:
        path = Path.cwd()

    # Validate path
    if not path.exists():
        console.print(f"[red]Error: Path does not exist: {path}[/red]")
        raise typer.Exit(code=1)

    if not path.is_dir():
        console.print(f"[red]Error: Path is not a directory: {path}[/red]")
        raise typer.Exit(code=1)

    # Perform scan
    scanner = RepoScanner()

    try:
        result = scanner.scan_directory(
            path=path,
            ignore_file=ignore_file,
        )
    except Exception as e:
        console.print(f"[red]Error scanning directory: {e}[/red]")
        raise typer.Exit(code=1)

    # Output
    if json_output:
        import json

        output = {
            "path": str(path),
            "total_tokens": result.total_tokens,
            "total_lines": result.total_lines,
            "total_files": result.total_files,
            "ignored_files": result.ignored_files,
            "files": [
                {
                    "path": str(f.path.relative_to(path)),
                    "tokens": f.tokens,
                    "lines": f.lines,
                }
                for f in result.files
            ],
        }
        console.print_json(json.dumps(output, indent=2))
        return

    # Rich output
    if not verbose:
        # Summary only
        estimated_cost = result.estimate_cost()
        console.print(f"\n[bold cyan]Scanning {path.name}/...[/bold cyan]\n")
        console.print(f"[bold]Total:[/bold]     {result.total_tokens:,} tokens")
        console.print(f"[bold]Lines:[/bold]     {result.total_lines:,}")
        console.print(f"[bold]Files:[/bold]     {result.total_files}")
        console.print(f"[bold]Ignored:[/bold]  {result.ignored_files}")
        console.print(f"[bold]Cost:[/bold]     ~${estimated_cost:.4f}/run (GPT-4)\n")
    else:
        # Per-file breakdown
        console.print(f"\n[bold cyan]Scanning {path.name}/...[/bold cyan]\n")

        # Create table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("File", style="dim")
        table.add_column("Tokens", justify="right")
        table.add_column("Lines", justify="right")

        # Sort by tokens descending
        sorted_files = sorted(result.files, key=lambda f: f.tokens, reverse=True)

        for file_result in sorted_files:
            rel_path = file_result.path.relative_to(path)
            # Format with color based on size
            if file_result.tokens > 5000:
                token_style = "bold red"
            elif file_result.tokens > 2000:
                token_style = "yellow"
            elif file_result.tokens > 500:
                token_style = "green"
            else:
                token_style = "dim"

            table.add_row(
                str(rel_path),
                Text(f"{file_result.tokens:,}", style=token_style),
                f"{file_result.lines:,}",
            )

        console.print(table)

        # Summary panel
        estimated_cost = result.estimate_cost()
        summary = Text()
        summary.append(f"Total: ", style="bold")
        summary.append(f"{result.total_tokens:,} tokens\n")
        summary.append(f"Lines: ", style="bold")
        summary.append(f"{result.total_lines:,}\n")
        summary.append(f"Files: ", style="bold")
        summary.append(f"{result.total_files}\n")
        summary.append(f"Ignored: ", style="bold")
        summary.append(f"{result.ignored_files}\n")
        summary.append(f"Estimated cost: ", style="bold")
        summary.append(f"${estimated_cost:.4f}/run (GPT-4)", style="green")

        console.print(Panel(summary, title="[bold]Summary[/bold]", border_style="cyan"))
