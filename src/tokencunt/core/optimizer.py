"""Prompt optimizer module."""

import re
from typing import Optional


class PromptOptimizer:
    """
    Reduce prompt size through various techniques.
    
    Techniques:
    - Remove redundant whitespace
    - Truncate to max tokens
    - Remove duplicate sentences
    """
    
    def __init__(self, max_tokens: Optional[int] = None):
        """
        Initialize prompt optimizer.
        
        Args:
            max_tokens: Maximum tokens to allow (truncates if exceeded)
        """
        self.max_tokens = max_tokens
    
    def optimize(self, prompt: str) -> str:
        """
        Apply all optimization techniques.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Optimized prompt
        """
        prompt = self._remove_redundant_whitespace(prompt)
        prompt = self._remove_duplicate_sentences(prompt)
        
        if self.max_tokens:
            prompt = self._truncate_to_tokens(prompt)
        
        return prompt
    
    def _remove_redundant_whitespace(self, text: str) -> str:
        """Remove redundant spaces, tabs, newlines."""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove trailing/leading whitespace per line
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(line for line in lines if line)
    
    def _remove_duplicate_sentences(self, text: str) -> str:
        """Remove duplicate sentences."""
        # Split by common sentence delimiters
        sentences = re.split(r'(?<=[.!?])\s+', text)
        seen = set()
        result = []
        
        for sentence in sentences:
            # Normalize for comparison
            normalized = sentence.lower().strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(sentence)
        
        return ' '.join(result)
    
    def _truncate_to_tokens(self, text: str, ratio: float = 0.9) -> str:
        """Truncate text to fit within token budget."""
        if not self.max_tokens:
            return text
        
        # Rough estimate: 4 characters per token
        max_chars = int(self.max_tokens * ratio * 4)
        
        if len(text) <= max_chars:
            return text
        
        # Truncate and add indicator
        return text[:max_chars] + "... [truncated]"
    
    def estimate_savings(self, original: str, optimized: str) -> float:
        """
        Calculate percentage savings.
        
        Args:
            original: Original prompt
            optimized: Optimized prompt
            
        Returns:
            Percentage savings
        """
        original_len = len(original)
        optimized_len = len(optimized)
        
        if original_len == 0:
            return 0.0
        
        return (original_len - optimized_len) / original_len * 100
