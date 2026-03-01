"""Request batcher module."""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class BatchedRequest:
    """A single request to be batched."""
    id: str
    messages: list
    kwargs: dict


class RequestBatcher:
    """
    Combine multiple requests into batches.
    
    Strategies:
    - By token count (max tokens per batch)
    - By request count (max requests per batch)
    """
    
    def __init__(self, max_tokens: int = 100000, max_requests: int = 10):
        """
        Initialize request batcher.
        
        Args:
            max_tokens: Maximum tokens per batch
            max_requests: Maximum requests per batch
        """
        self.max_tokens = max_tokens
        self.max_requests = max_requests
        self.pending: List[BatchedRequest] = []
        self.current_tokens = 0
    
    def add(self, request: BatchedRequest) -> bool:
        """
        Add request to batch.
        
        Args:
            request: Request to add
            
        Returns:
            True if batch is ready to flush, False otherwise
        """
        estimated_tokens = self._estimate_tokens(request.messages)
        
        # Check if adding would exceed limits
        if (self.current_tokens + estimated_tokens > self.max_tokens or
            len(self.pending) >= self.max_requests):
            return False  # Batch is full
        
        self.pending.append(request)
        self.current_tokens += estimated_tokens
        return True
    
    def flush(self) -> List[List[BatchedRequest]]:
        """
        Flush current batch and return list of batches.
        
        Returns:
            List of batches (each batch is a list of BatchedRequest)
        """
        if not self.pending:
            return []
        
        batches = []
        current_batch = []
        current_tokens = 0
        
        for request in self.pending:
            est = self._estimate_tokens(request.messages)
            if (current_tokens + est > self.max_tokens or
                len(current_batch) >= self.max_requests):
                if current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_tokens = 0
            
            current_batch.append(request)
            current_tokens += est
        
        if current_batch:
            batches.append(current_batch)
        
        self.pending = []
        self.current_tokens = 0
        
        return batches
    
    def _estimate_tokens(self, messages: list) -> int:
        """Rough token estimation for batching."""
        # ~4 chars per token as rough estimate
        total_chars = sum(len(m.get("content", "")) for m in messages)
        return total_chars // 4
    
    def clear(self):
        """Clear pending requests without returning them."""
        self.pending = []
        self.current_tokens = 0
    
    @property
    def is_empty(self) -> bool:
        """Check if batcher has no pending requests."""
        return len(self.pending) == 0
    
    @property
    def size(self) -> int:
        """Get number of pending requests."""
        return len(self.pending)
