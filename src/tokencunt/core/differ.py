"""Prompt differ module - Git-style diff for prompt changes."""

import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tokencunt.core.token_counter import TokenCounter


# Default MiniMax M2.5 pricing (can be customized)
DEFAULT_INPUT_COST_PER_1K = 0.001  # $0.001 per 1K input tokens
DEFAULT_OUTPUT_COST_PER_1K = 0.003  # $0.003 per 1K output tokens


@dataclass
class DiffStats:
    """Statistics from comparing two prompts."""

    original_tokens: int
    optimized_tokens: int
    tokens_saved: int
    percent_saved: float
    original_cost: float
    optimized_cost: float
    cost_saved: float


class PromptDiffer:
    """Compute and format differences between prompts."""

    def __init__(
        self,
        model: str = "gpt-4",
        input_cost_per_1k: float = DEFAULT_INPUT_COST_PER_1K,
        output_cost_per_1k: float = DEFAULT_OUTPUT_COST_PER_1K,
    ):
        """
        Initialize the prompt differ.

        Args:
            model: Model name for token counting
            input_cost_per_1k: Cost per 1K input tokens
            output_cost_per_1k: Cost per 1K output tokens
        """
        self.token_counter = TokenCounter(model=model)
        self.input_cost_per_1k = input_cost_per_1k
        self.output_cost_per_1k = output_cost_per_1k

    def load_file(self, path: str | Path) -> str:
        """
        Load prompt from file.

        Args:
            path: Path to the file

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return file_path.read_text(encoding="utf-8")

    def compute_diff(
        self,
        original_prompt: str,
        optimized_prompt: str,
        original_name: str = "original.txt",
        optimized_name: str = "optimized.txt",
    ) -> list[str]:
        """
               Compute differences between two prompts.

               Args:
                   original_prompt: Original prompt_prompt: Optimized prompt text
        text
                   optimized            original_name: Name for original file in diff header
                   optimized_name: Name for optimized file in diff header

               Returns:
                   List of diff lines in unified format
        """
        original_lines = original_prompt.splitlines(keepends=True)
        optimized_lines = optimized_prompt.splitlines(keepends=True)

        # Use unified_diff to create git-style diff
        diff = difflib.unified_diff(
            original_lines,
            optimized_lines,
            fromfile=original_name,
            tofile=optimized_name,
            lineterm="",
        )

        return list(diff)

    def format_unified_diff(
        self,
        original_prompt: str,
        optimized_prompt: str,
        original_name: str = "original.txt",
        optimized_name: str = "optimized.txt",
    ) -> str:
        """
        Format differences in unified diff format (like git diff).

        Args:
            original_prompt: Original prompt text
            optimized_prompt: Optimized prompt text
            original_name: Name for original file in diff header
            optimized_name: Name for optimized file in diff header

        Returns:
            Formatted diff string
        """
        diff_lines = self.compute_diff(
            original_prompt, optimized_prompt, original_name, optimized_name
        )
        return "".join(diff_lines)

    def compute_stats(
        self,
        original_prompt: str,
        optimized_prompt: str,
    ) -> DiffStats:
        """
        Compute token count comparison and savings.

        Args:
            original_prompt: Original prompt text
            optimized_prompt: Optimized prompt text

        Returns:
            DiffStats with token counts and savings
        """
        original_tokens = self.token_counter.estimate(original_prompt)
        optimized_tokens = self.token_counter.estimate(optimized_prompt)

        tokens_saved = original_tokens - optimized_tokens
        percent_saved = (
            (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
        )

        original_cost = self._calculate_cost(original_tokens)
        optimized_cost = self._calculate_cost(optimized_tokens)
        cost_saved = original_cost - optimized_cost

        return DiffStats(
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            tokens_saved=tokens_saved,
            percent_saved=percent_saved,
            original_cost=original_cost,
            optimized_cost=optimized_cost,
            cost_saved=cost_saved,
        )

    def _calculate_cost(self, tokens: int) -> float:
        """
        Calculate cost for tokens.

        Args:
            tokens: Number of tokens

        Returns:
            Estimated cost in USD
        """
        # Assume 80% input, 20% output for estimation
        input_tokens = int(tokens * 0.8)
        output_tokens = int(tokens * 0.2)
        return (input_tokens / 1000) * self.input_cost_per_1k + (
            output_tokens / 1000
        ) * self.output_cost_per_1k

    def format_stats(self, stats: DiffStats) -> str:
        """
        Format statistics as a string.

        Args:
            stats: DiffStats to format

        Returns:
            Formatted statistics string
        """
        # Format token counts with commas
        orig_tokens = f"{stats.original_tokens:,}"
        opt_tokens = f"{stats.optimized_tokens:,}"

        # Format percentage with ASCII-safe indicator
        if stats.percent_saved > 0:
            percent_indicator = f"(-{stats.percent_saved:.1f}%)"
        elif stats.percent_saved < 0:
            percent_indicator = f"(+{abs(stats.percent_saved):.1f}%)"
        else:
            percent_indicator = "(0%)"

        # Format costs
        orig_cost = f"${stats.original_cost:.3f}"
        opt_cost = f"${stats.optimized_cost:.3f}"

        if stats.cost_saved > 0:
            cost_indicator = f"(-${stats.cost_saved:.3f})"
        elif stats.cost_saved < 0:
            cost_indicator = f"(+${abs(stats.cost_saved):.3f})"
        else:
            cost_indicator = "$0.000"

        # Use ASCII-safe arrow
        return f"Tokens: {orig_tokens} -> {opt_tokens} ({percent_indicator})\nCost: {orig_cost} -> {opt_cost} ({cost_indicator})"

    def diff(
        self,
        original_prompt: str,
        optimized_prompt: str,
        original_name: str = "original.txt",
        optimized_name: str = "optimized.txt",
        include_stats: bool = True,
    ) -> dict:
        """
        Compute complete diff with statistics.

        Args:
            original_prompt: Original prompt text
            optimized_prompt: Optimized prompt text
            original_name: Name for original file in diff header
            optimized_name: Name for optimized file in diff header
            include_stats: Whether to include statistics

        Returns:
            Dictionary with diff and stats
        """
        result = {
            "original_name": original_name,
            "optimized_name": optimized_name,
            "diff": self.format_unified_diff(
                original_prompt, optimized_prompt, original_name, optimized_name
            ),
        }

        if include_stats:
            stats = self.compute_stats(original_prompt, optimized_prompt)
            result["stats"] = stats
            result["stats_formatted"] = self.format_stats(stats)

        return result
