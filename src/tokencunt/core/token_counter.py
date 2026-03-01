"""Token counter module for estimation and tracking."""

import tiktoken
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenUsage:
    """Token usage information."""
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens
    
    def add(self, other: "TokenUsage"):
        """Add another TokenUsage to this one."""
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens


class TokenCounter:
    """Token estimation and tracking using tiktoken."""
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize token counter.
        
        Args:
            model: Model name for encoding (default: gpt-4)
                   MiniMax uses same encoding as GPT-4
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def estimate(self, text: str) -> int:
        """
        Estimate tokens for plain text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(self.encoding.encode(text))
    
    def estimate_messages(self, messages: list[dict]) -> int:
        """
        Estimate tokens for chat messages.
        
        Includes formatting overhead (~3-4 tokens per message for
        <|im_start|>, role, <|im_end|> tokens).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Estimated token count
        """
        # Base tokens: <|im_start|>system<|im_end|>
        tokens = 3
        # Per-message tokens: <|im_start|>, role, <|im_end|>
        tokens_per_message = 3
        
        for message in messages:
            tokens += tokens_per_message
            tokens += self.estimate(message.get("content", ""))
            tokens += self.estimate(message.get("role", ""))
            # Add function call tokens if present
            if "function_call" in message:
                tokens += self.estimate(str(message["function_call"]))
        
        return tokens
    
    def count(self, text: str) -> int:
        """
        Exact count (alias for estimate).
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        return self.estimate(text)
    
    def parse_usage(self, response) -> TokenUsage:
        """
        Parse token usage from API response.
        
        Args:
            response: API response object with .usage attribute
            
        Returns:
            TokenUsage with input and output token counts
        """
        usage = response.usage
        return TokenUsage(
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens
        )
    
    def estimate_cost(
        self,
        tokens: int,
        input_cost_per_1k: float = 0.001,
        output_cost_per_1k: float = 0.003
    ) -> float:
        """
        Estimate cost for token count.
        
        Args:
            tokens: Number of tokens
            input_cost_per_1k: Cost per 1K input tokens (default: $0.001)
            output_cost_per_1k: Cost per 1K output tokens (default: $0.003)
            
        Returns:
            Estimated cost in USD
        """
        return (tokens / 1000) * input_cost_per_1k
