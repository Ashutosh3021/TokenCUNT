"""Rich formatters for CLI output."""

from typing import Any, Optional, Dict
from decimal import Decimal
from typing import Any, Dict, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown


class OutputFormatter:
    """Output formatter with Rich for beautiful terminal output."""

    def __init__(
        self,
        quiet: bool = False,
        verbose: bool = False,
        json_output: bool = False,
        debug: bool = False,
    ):
        self.quiet = quiet
        self.verbose = verbose
        self.json_output = json_output
        self.debug = debug
        self.console = Console(color_system="auto", stderr=self.verbose)

    def success(self, message: str) -> None:
        """Print success message."""
        if not self.quiet:
            self.console.print(f"[bold green]OK[/bold green] {message}")

    def error(self, message: str, suggestion: Optional[str] = None) -> None:
        """Print error message."""
        if suggestion:
            self.console.print(f"[bold red]X[/bold red] {message}")
            if not self.quiet:
                self.console.print(f"[dim]Suggestion: {suggestion}[/dim]")
        else:
            self.console.print(f"[bold red]X[/bold red] {message}")

    def warning(self, message: str) -> None:
        """Print warning message."""
        if not self.quiet:
            self.console.print(f"[bold yellow]![/bold yellow] {message}")

    def info(self, message: str) -> None:
        """Print info message."""
        if not self.quiet and not self.verbose:
            self.console.print(message)
        elif self.verbose:
            self.console.print(f"[dim]{message}[/dim]")

    def print_response(self, content: str, format: str = "text") -> None:
        """Print API response content."""
        if self.json_output:
            import json

            self.console.print_json(content)
        elif format == "markdown":
            self.console.print(Markdown(content))
        elif format == "code":
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            self.console.print(syntax)
        else:
            self.console.print(content)

    def format_token_cost(
        self,
        estimated: int,
        actual: Optional[int] = None,
    ) -> Table:
        """Format token cost as a table."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("label", style="cyan")
        table.add_column("value", style="white")

        table.add_row("Estimated:", f"{estimated:,}")

        if actual is not None:
            table.add_row("Actual:", f"{actual:,}")
            diff = actual - estimated
            diff_str = f"+{diff:,}" if diff > 0 else f"{diff:,}"
            diff_style = "red" if diff > estimated * 0.5 else "green"
            table.add_row("Difference:", f"[{diff_style}]{diff_str}[/{diff_style}]")

        return table

    def format_budget_status(
        self,
        used: Union[int, Decimal],
        limit: Union[int, Decimal],
    ) -> Table:
        """Format budget status as a table."""
        # Convert to Decimal for calculations
        used = Decimal(str(used))
        limit = Decimal(str(limit))

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("label", style="cyan")
        table.add_column("value", style="white")

        percentage = (used / limit * 100) if limit > 0 else Decimal("0")
        table.add_row("Used:", f"{used:,} tokens")
        table.add_row("Limit:", f"{limit:,} tokens")

        if percentage >= 100:
            style = "bold red"
        elif percentage >= 80:
            style = "bold yellow"
        else:
            style = "green"

        table.add_row("Percentage:", f"[{style}]{percentage:.1f}%[/{style}]")

        return table

    def error_panel(
        self,
        title: str,
        message: str,
        suggestion: Optional[str] = None,
    ) -> Panel:
        """Create an error panel."""
        content = f"[bold red]{message}[/bold red]"
        if suggestion:
            content += f"\n\n[dim]Suggestion: {suggestion}[/dim]"
        return Panel(content, title=title, border_style="red")

    def response_panel(
        self,
        content: str,
        title: str = "Response",
        format: str = "text",
    ) -> Panel:
        """Create a response panel."""
        if format == "markdown":
            return Panel(
                Markdown(content),
                title=title,
                border_style="green",
                padding=(1, 2),
            )
        elif format == "code":
            syntax = Syntax(content, "python", theme="monokai")
            return Panel(
                syntax,
                title=title,
                border_style="green",
                padding=(1, 1),
            )
        else:
            return Panel(
                content,
                title=title,
                border_style="green",
                padding=(1, 2),
            )

    def print_table(self, table: Table) -> None:
        """Print a Rich table."""
        self.console.print(table)

    def print_panel(self, panel: Panel) -> None:
        """Print a Rich panel."""
        self.console.print(panel)

    def debug_info(self, data: Dict[str, Any]) -> None:
        """Print debug information."""
        if self.debug or self.verbose:
            import json

            self.console.print("[dim]")
            self.console.print_json(json.dumps(data, default=str, indent=2))
            self.console.print("[/dim]")
