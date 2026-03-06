"""Scan command - Scan repository for token estimation."""

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_ERROR, EXIT_INVALID_ARGS
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core.scanner import RepoScanner, ScanResult


# Default extensions to scan
DEFAULT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".txt",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".env",
    ".sh",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
}


@app.command(name="scan")
def scan_command(
    path: Annotated[
        Optional[Path],
        typer.Argument(
            help="Directory or file to scan (default: current directory)",
        ),
    ] = None,
    extensions: Annotated[
        Optional[str],
        typer.Option(
            "--extensions",
            "-e",
            help="Comma-separated list of file extensions to include (e.g., py,js,ts)",
        ),
    ] = None,
    ignore_file: Annotated[
        Optional[Path],
        typer.Option(
            "--ignore",
            help="Path to .tokencuntignore file",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output results as JSON"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show per-file breakdown"),
    ] = False,
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Scan a repository and estimate token counts.

    Scans the specified directory (or current directory) for source files
    and provides token estimates based on file content.

    Examples:

        Scan current directory:
        $ ts scan

        Scan specific directory:
        $ ts scan ./src

        Scan with specific extensions:
        $ ts scan --extensions py,js,ts

        Scan with verbose output:
        $ ts scan -v

        Output JSON:
        $ ts scan --json
    """
    # Get global options from context
    state = ctx.obj if ctx.obj else None
    quiet = state.quiet if state else False
    json_output = json_output or (state.json_output if state else False)
    verbose = verbose or (state.verbose if state else False)
    debug = state.debug if state else False

    formatter = OutputFormatter(
        quiet=quiet,
        verbose=verbose,
        json_output=json_output,
        debug=debug,
    )

    # Default to current directory
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path)

    # Validate path
    if not path.exists():
        formatter.error(f"Path does not exist: {path}")
        return EXIT_INVALID_ARGS

    # Parse extensions if provided
    ext_set = None
    if extensions:
        ext_set = {f".{ext.strip().lstrip('.')}" for ext in extensions.split(",")}

    # Initialize scanner
    scanner = RepoScanner(extensions=ext_set)

    # Load ignore file if provided
    if ignore_file:
        ignore_path = Path(ignore_file)
        if ignore_path.exists():
            scanner.load_ignore_file(ignore_path)
            if not quiet:
                formatter.info(f"Loaded ignore patterns from {ignore_path}")
        else:
            formatter.warning(f"Ignore file not found: {ignore_file}")

    # Perform scan
    try:
        if not quiet:
            formatter.info(f"Scanning {path}...")

        result = scanner.scan_directory(path)

        if result.total_files == 0:
            formatter.warning("No supported files found")
            return EXIT_SUCCESS

        # Output results
        if json_output:
            return _output_json(formatter, result, path)
        else:
            return _output_formatted(formatter, result, path, verbose)

    except Exception as e:
        formatter.error(f"Scan failed: {e}")
        if debug:
            formatter.debug_info({"error": str(e)})
        return EXIT_ERROR


def _output_json(
    formatter: OutputFormatter,
    result: ScanResult,
    path: Path,
) -> int:
    """Output results as JSON."""
    import json

    output = {
        "path": str(path),
        "total_files": result.total_files,
        "total_tokens": result.total_tokens,
        "total_lines": result.total_lines,
        "total_size_bytes": result.total_size_bytes,
        "estimated_cost_usd": round(result.estimated_cost, 4),
        "files_by_extension": result.files_by_extension,
        "tokens_by_extension": result.tokens_by_extension,
        "files": [
            {
                "path": str(f.path.relative_to(path)),
                "tokens": f.tokens,
                "lines": f.lines,
                "size_bytes": f.size_bytes,
            }
            for f in result.files
        ],
    }

    formatter.console.print(json.dumps(output, indent=2))
    return EXIT_SUCCESS


def _output_formatted(
    formatter: OutputFormatter,
    result: ScanResult,
    path: Path,
    verbose: bool,
) -> int:
    """Output results in formatted table."""
    from rich.table import Table
    from rich.panel import Panel

    # Summary panel
    summary = f"""[bold]Total Files:[/bold] {result.total_files:,}
[bold]Total Tokens:[/bold] {result.total_tokens:,}
[bold]Total Lines:[/bold] {result.total_lines:,}
[bold]Total Size:[/bold] {result.total_size_bytes:,} bytes
[bold]Estimated Cost:[/bold] ${result.estimated_cost:.4f}"""

    formatter.console.print(Panel(summary, title="[bold cyan]Scan Results[/bold cyan]"))

    # Files by extension table
    if result.files_by_extension:
        ext_table = Table(title="Tokens by Extension", show_header=True)
        ext_table.add_column("Extension", style="cyan")
        ext_table.add_column("Files", justify="right")
        ext_table.add_column("Tokens", justify="right")

        for ext, count in sorted(
            result.tokens_by_extension.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            file_count = result.files_by_extension[ext]
            ext_table.add_row(ext, f"{file_count:,}", f"{count:,}")

        formatter.console.print("")
        formatter.print_table(ext_table)

    # Per-file breakdown (verbose mode)
    if verbose and result.files:
        file_table = Table(
            title="Per-File Breakdown",
            show_header=True,
        )
        file_table.add_column("File", style="cyan", no_wrap=False)
        file_table.add_column("Tokens", justify="right")
        file_table.add_column("Lines", justify="right")
        file_table.add_column("Size", justify="right")

        for f in sorted(result.files, key=lambda x: x.tokens, reverse=True)[:50]:
            rel_path = f.path.relative_to(path)
            size_str = _format_size(f.size_bytes)
            file_table.add_row(
                str(rel_path)[:50],
                f"{f.tokens:,}",
                f"{f.lines:,}",
                size_str,
            )

        formatter.console.print("")
        formatter.print_table(file_table)

        if len(result.files) > 50:
            formatter.info(f"Showing top 50 of {len(result.files)} files")

    return EXIT_SUCCESS


def _format_size(size_bytes: int) -> str:
    """Format byte size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
