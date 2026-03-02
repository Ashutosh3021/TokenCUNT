"""Typer CLI application with global options."""

from typing import Optional
from pathlib import Path

import typer
from typing_extensions import Annotated

from tokencunt.cli.exit_codes import EXIT_SUCCESS


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
    typer.echo("TokenCUNT v0.1.0")


if __name__ == "__main__":
    app()
