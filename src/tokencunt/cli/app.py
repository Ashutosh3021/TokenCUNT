"""Typer CLI application with global options."""

from typing import Optional
from pathlib import Path

import typer
from typing_extensions import Annotated

from tokencunt.cli.exit_codes import EXIT_SUCCESS
from tokencunt.cli.logo import LOGO, VERSION, TAGLINE


# Global state stored in typer.Context.obj
class CLIState:
    """Shared CLI state."""

    def __init__(
        self,
        quiet: bool = False,
        verbose: bool = False,
        json_output: bool = False,
        debug: bool = False,
        config: Optional[Path] = None,
        yes: bool = False,
    ):
        self.quiet = quiet
        self.verbose = verbose
        self.json_output = json_output
        self.debug = debug
        self.config = config
        self.yes = yes


# Create main Typer app
app = typer.Typer(
    name="ts",
    help="TokenCUNT - Token counting and budget management for MiniMax API",
    add_completion=False,
)


@app.callback(
    invoke_without_command=True,
    context_settings={"allow_interspersed_args": False},
)
def cli_main(
    ctx: typer.Context,
    quiet: Annotated[
        bool, typer.Option("-q", "--quiet", help="Minimal output")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("-v", "--verbose", help="Verbose output")
    ] = False,
    json_output: Annotated[bool, typer.Option("--json", help="JSON output")] = False,
    debug: Annotated[
        bool, typer.Option("--debug", help="Debug mode with traceback")
    ] = False,
    config: Annotated[
        Optional[Path], typer.Option("--config", help="Custom config file")
    ] = None,
    yes: Annotated[
        bool, typer.Option("-y", "--yes", help="Skip confirmations")
    ] = False,
) -> None:
    """Global options for all commands."""
    ctx.obj = CLIState(
        quiet=quiet,
        verbose=verbose,
        json_output=json_output,
        debug=debug,
        config=config,
        yes=yes,
    )


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(VERSION)


@app.command()
def start() -> None:
    """Show TokenCUNT logo and welcome message."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text

        console = Console()
        logo_text = Text(LOGO, style="cyan")
        console.print(
            Panel(logo_text, title="[bold cyan]TokenCUNT[/bold cyan]", subtitle=TAGLINE)
        )
    except Exception:
        # Fallback if Rich fails
        typer.echo(LOGO)
        typer.echo(TAGLINE)

    typer.echo("\nGet started:")
    typer.echo("  ts --help       Show all commands")
    typer.echo("  ts ask          Ask a question")
    typer.echo("  ts analyze      Analyze a file")
    typer.echo("  ts batch        Process batch tasks")
    typer.echo("  ts report       View usage report")


if __name__ == "__main__":
    # Import commands to register them with the app
    from tokencunt.cli import commands  # noqa: F401

    app()
