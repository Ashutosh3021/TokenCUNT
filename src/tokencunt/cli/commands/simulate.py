"""Simulate command - Calculate estimated costs based on traffic patterns."""

from typing import Optional

import typer
from typing_extensions import Annotated

from tokencunt.cli import app
from tokencunt.cli.exit_codes import EXIT_SUCCESS, EXIT_INVALID_ARGS
from tokencunt.cli.formatters import OutputFormatter
from tokencunt.core.simulator import CostSimulator, MODEL_PRICING, SCENARIOS


@app.command(name="simulate")
def simulate_command(
    requests: Annotated[
        Optional[int],
        typer.Option(
            "--requests",
            "-r",
            help="Number of requests per day",
        ),
    ] = None,
    tokens: Annotated[
        Optional[int],
        typer.Option(
            "--tokens",
            "-t",
            help="Average tokens per request",
        ),
    ] = None,
    scenario: Annotated[
        Optional[str],
        typer.Option(
            "--scenario",
            "-s",
            help="Pre-defined scenario (dev, startup, enterprise)",
        ),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help=f"Model to simulate (default: gpt-4). Available: {', '.join(MODEL_PRICING.keys())}",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output results as JSON"),
    ] = False,
    ctx: typer.Context = typer.Option(None),
) -> int:
    """Simulate API costs based on traffic patterns.

    Calculate monthly costs for LLM API usage based on:
    - Number of requests per day
    - Average tokens per request
    - Selected model

    Examples:

        Calculate cost for custom traffic:
        $ ts simulate --requests 1000 --tokens 500

        Use pre-defined scenario:
        $ ts simulate --scenario startup --model gpt-4

        Output as JSON:
        $ ts simulate --requests 500 --tokens 1000 --json
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

    # Initialize simulator
    simulator = CostSimulator(model=model)

    # Validate inputs
    if scenario:
        # Scenario mode
        if scenario not in SCENARIOS:
            formatter.error(
                f"Unknown scenario: {scenario}. Available: {', '.join(SCENARIOS.keys())}"
            )
            return EXIT_INVALID_ARGS

        # Get scenario details
        scenario_data = SCENARIOS[scenario]

        # Run scenario
        try:
            result = simulator.simulate_scenario(scenario, model=model)
        except ValueError as e:
            formatter.error(str(e))
            return EXIT_INVALID_ARGS

        scenario_name = result["scenario"]

    else:
        # Custom traffic mode - require both params
        if requests is None or tokens is None:
            formatter.error(
                "Either --scenario or both --requests and --tokens required"
            )
            formatter.info("Examples:")
            formatter.info("  ts simulate --requests 1000 --tokens 500")
            formatter.info("  ts simulate --scenario startup")
            return EXIT_INVALID_ARGS

        # Validate inputs
        if requests < 0:
            formatter.error("--requests must be non-negative")
            return EXIT_INVALID_ARGS
        if tokens < 0:
            formatter.error("--tokens must be non-negative")
            return EXIT_INVALID_ARGS

        # Run custom simulation
        result = simulator.simulate_traffic(
            requests_per_day=requests,
            avg_tokens_per_request=tokens,
            model=model,
        )
        scenario_name = "Custom Traffic"

    # Output results
    if json_output:
        return _output_json(formatter, result)
    else:
        return _output_formatted(formatter, result, scenario_name)


def _output_json(formatter: OutputFormatter, result: dict) -> int:
    """Output results as JSON."""
    import json

    output = {
        "scenario": result["scenario"],
        "model": result["model"],
        "requests_per_day": result["requests_per_day"],
        "tokens_per_request": result["avg_tokens_per_request"],
        "monthly_requests": result["monthly_requests"],
        "monthly_tokens": result["monthly_total_tokens"],
        "monthly_input_tokens": result["monthly_input_tokens"],
        "monthly_output_tokens": result["monthly_output_tokens"],
        "cost_per_1k_input": result["cost_per_1k_input"],
        "cost_per_1k_output": result["cost_per_1k_output"],
        "monthly_input_cost": result["monthly_input_cost"],
        "monthly_output_cost": result["monthly_output_cost"],
        "estimated_monthly_cost": result["monthly_total_cost"],
        "tier": result["tier"],
    }

    formatter.console.print(json.dumps(output, indent=2))
    return EXIT_SUCCESS


def _output_formatted(
    formatter: OutputFormatter, result: dict, scenario_name: str
) -> int:
    """Output results in formatted table."""
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text

    # Build the output
    lines = []

    # Scenario header
    lines.append(f"[bold cyan]Scenario:[/bold cyan] {scenario_name}")
    lines.append("")
    lines.append("-" * 30)

    # Traffic details
    lines.append(f"[bold]Requests/day:[/bold]     {result['requests_per_day']:,}")
    lines.append(f"[bold]Tokens/req:[/bold]       {result['avg_tokens_per_request']:,}")
    lines.append("")
    lines.append("-" * 30)

    # Monthly totals
    lines.append(f"[bold]Monthly Requests:[/bold] {result['monthly_requests']:,}")
    lines.append(f"[bold]Monthly Tokens:[/bold]   {result['monthly_total_tokens']:,}")
    lines.append("")
    lines.append("-" * 30)

    # Model info
    lines.append(f"[bold]Model:[/bold] {result['model'].upper()}")
    lines.append(
        f"[bold]Cost/1K tokens:[/bold]   ${result['cost_per_1k_input']:.4f} in / ${result['cost_per_1k_output']:.4f} out"
    )
    lines.append("")
    lines.append("-" * 30)

    # Final cost (emphasized)
    lines.append("")
    lines.append(
        f"[bold green]Estimated Cost:[/bold green]   [bold green]${result['monthly_total_cost']:.2f}/month[/bold green]"
    )

    # Print as panel
    formatter.console.print(
        Panel(
            "\n".join(lines),
            title="[bold cyan]Cost Simulator[/bold cyan]",
            border_style="cyan",
        )
    )

    # Also show breakdown table
    table = Table(title="Cost Breakdown", show_header=False, box=None)
    table.add_column("Label", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Input tokens", f"{result['monthly_input_tokens']:,}")
    table.add_row(
        f"  @ ${result['cost_per_1k_input']:.4f}/1K",
        f"${result['monthly_input_cost']:.4f}",
    )
    table.add_row("Output tokens", f"{result['monthly_output_tokens']:,}")
    table.add_row(
        f"  @ ${result['cost_per_1k_output']:.4f}/1K",
        f"${result['monthly_output_cost']:.4f}",
    )
    table.add_row("", "")
    table.add_row(
        "[bold]Total[/bold]", f"[bold]${result['monthly_total_cost']:.2f}[/bold]"
    )

    formatter.console.print("")
    formatter.print_table(table)

    return EXIT_SUCCESS
