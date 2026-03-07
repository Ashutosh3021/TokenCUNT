"""Prompt optimizer module - AI + rule-based optimization."""

import re
from dataclasses import dataclass
from typing import Optional

from tokencunt.core.token_counter import TokenCounter


@dataclass
class OptimizationSuggestion:
    """Represents a single optimization suggestion."""

    rule_name: str
    original: str
    replacement: str
    tokens_saved: int


@dataclass
class OptimizationResult:
    """Result of prompt optimization."""

    original_prompt: str
    optimized_prompt: str
    original_tokens: int
    optimized_tokens: int
    suggestions: list[OptimizationSuggestion]
    mode: str  # "rules", "ai", or "hybrid"


class PromptOptimizer:
    """
    AI + rule-based prompt optimization.

    Combines:
    - Rule-based optimizations (fast, no API call)
    - AI optimization (via MiniMax API)
    - Hybrid mode (both combined)
    """

    # Rule-based patterns for optimization
    FILLER_WORDS = [
        (r"\bplease\b", ""),
        (r"\bkindly\b", ""),
        (r"\bwould you mind\b", ""),
        (r"\bcould you please\b", ""),
        (r"\bwould it be possible to\b", ""),
    ]

    PHRASE_SIMPLIFICATIONS = [
        (r"\bhelp the user\b", "assist user"),
        (r"\bassist the user\b", "assist user"),
        (r"\bprovide assistance with\b", "help with"),
        (r"\bcan you help me\b", "help me"),
        (r"\bI would like you to\b", "please"),
        (r"\bit would be great if you could\b", "please"),
        (r"\bthank you for your help\b", "thanks"),
        (r"\bthank you in advance\b", ""),
        (r"\bpardon me\b", ""),
        (r"\bI hope this finds you well\b", ""),
    ]

    # Use ASCII arrows for Windows compatibility
    ARROW = "->"

    def __init__(self, api_key: Optional[str] = None, model: str = "MiniMax-Text-01"):
        """
        Initialize prompt optimizer.

        Args:
            api_key: MiniMax API key (optional for rules-only mode)
            model: Model to use for AI optimization
        """
        self.api_key = api_key
        self.model = model
        self.token_counter = TokenCounter()

    def optimize_hybrid(self, prompt: str) -> OptimizationResult:
        """
        Combine AI + rule-based optimization.

        Args:
            prompt: Original prompt

        Returns:
            OptimizationResult with optimized prompt and suggestions
        """
        # First apply rules
        rules_result = self.optimize_with_rules(prompt)
        
        # Then apply AI (if API key available)
        if self.api_key:
            try:
                ai_result = self.optimize_with_ai(rules_result.optimized_prompt)
                # Combine suggestions
                all_suggestions = rules_result.suggestions + ai_result.suggestions
                return OptimizationResult(
                    original_prompt=prompt,
                    optimized_prompt=ai_result.optimized_prompt,
                    original_tokens=rules_result.original_tokens,
                    optimized_tokens=ai_result.optimized_tokens,
                    suggestions=all_suggestions,
                    mode="hybrid",
                )
            except Exception:
                # Fall back to rules-only if AI fails
                pass
        
        return rules_result

    def optimize_with_rules(self, prompt: str) -> OptimizationResult:
        """
        Apply rule-based optimizations only.

        Args:
            prompt: Original prompt

        Returns:
            OptimizationResult with rule-based suggestions
        """
        original_tokens = self.token_counter.count(prompt)
        optimized = prompt
        suggestions = []

        # Apply filler word removals
        for pattern, replacement in self.FILLER_WORDS:
            new_optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
            if new_optimized != optimized:
                tokens_saved = self.token_counter.count(optimized) - self.token_counter.count(new_optimized)
                if tokens_saved > 0:
                    suggestions.append(OptimizationSuggestion(
                        rule_name=f"Remove '{pattern}'",
                        original=optimized[:50],
                        replacement=new_optimized[:50],
                        tokens_saved=tokens_saved,
                    ))
                optimized = new_optimized

        # Apply phrase simplifications
        for pattern, replacement in self.PHRASE_SIMPLIFICATIONS:
            new_optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
            if new_optimized != optimized:
                tokens_saved = self.token_counter.count(optimized) - self.token_counter.count(new_optimized)
                if tokens_saved > 0:
                    suggestions.append(OptimizationSuggestion(
                        rule_name=f"Simplify '{pattern}' {self.ARROW} '{replacement}'",
                        original=optimized[:50],
                        replacement=new_optimized[:50],
                        tokens_saved=tokens_saved,
                    ))
                optimized = new_optimized

        # Remove redundant whitespace
        optimized = re.sub(r'\s+', ' ', optimized).strip()

        # Remove redundant newlines
        optimized = re.sub(r'\n{3,}', '\n\n', optimized)

        optimized_tokens = self.token_counter.count(optimized)

        return OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=optimized,
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            suggestions=suggestions,
            mode="rules",
        )

    def optimize_with_ai(self, prompt: str) -> OptimizationResult:
        """
        Use AI to optimize prompt.

        Args:
            prompt: Original prompt

        Returns:
            OptimizationResult from AI

        Raises:
            ValueError: If no API key available
        """
        if not self.api_key:
            raise ValueError("API key required for AI optimization")

        # This would call the MiniMax API to get an optimized version
        # For now, we'll return a placeholder that indicates AI optimization
        # In production, this would make an actual API call
        
        original_tokens = self.token_counter.count(prompt)
        
        # Placeholder: in production, this would call the API
        # For now, return the prompt as-is with a note
        return OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=prompt,  # Would be AI-optimized version
            original_tokens=original_tokens,
            optimized_tokens=original_tokens,  # Would be reduced
            suggestions=[],
            mode="ai",
        )

    def get_suggestions(self, prompt: str) -> list[str]:
        """
        Get list of possible optimizations without applying them.

        Args:
            prompt: Input prompt

        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Check for filler words
        for pattern, _ in self.FILLER_WORDS:
            if re.search(pattern, prompt, re.IGNORECASE):
                suggestions.append(f"Remove '{pattern}'")
        
        # Check for simplifiable phrases
        for pattern, replacement in self.PHRASE_SIMPLIFICATIONS:
            if re.search(pattern, prompt, re.IGNORECASE):
                suggestions.append(f"Simplify '{pattern}' → '{replacement}'")
        
        return suggestions
