"""Budget management module."""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class BudgetStatus(Enum):
    """Budget status levels."""
    OK = "ok"
    WARNING = "warning"  # 80% threshold
    EXCEEDED = "exceeded"


class BudgetConfig(BaseModel):
    """Budget configuration."""
    max_tokens: int = 100000
    warning_threshold: float = 0.8  # 80%


class BudgetManager:
    """Manages token budget enforcement and alerts."""
    
    def __init__(self, config: BudgetConfig = None):
        """
        Initialize budget manager.
        
        Args:
            config: Budget configuration
        """
        if config is None:
            config = BudgetConfig()
        self.config = config
        self.current_usage: int = 0
    
    def check_budget(self, estimated_tokens: int) -> tuple[BudgetStatus, Optional[str]]:
        """
        Check if request fits within budget.
        
        Args:
            estimated_tokens: Estimated tokens for the request
            
        Returns:
            Tuple of (status, warning_message)
        """
        projected = self.current_usage + estimated_tokens
        ratio = projected / self.config.max_tokens
        
        if ratio >= 1.0:
            return (BudgetStatus.EXCEEDED, 
                   f"Request would exceed budget: {projected}/{self.config.max_tokens} tokens")
        
        if ratio >= self.config.warning_threshold:
            return (BudgetStatus.WARNING,
                   f"Budget warning: {ratio*100:.0f}% used ({projected}/{self.config.max_tokens})")
        
        return (BudgetStatus.OK, None)
    
    def add_usage(self, tokens: int):
        """Add actual usage after API call."""
        self.current_usage += tokens
    
    @property
    def remaining(self) -> int:
        """Get remaining budget."""
        return self.config.max_tokens - self.current_usage
    
    @property
    def usage_ratio(self) -> float:
        """Get usage ratio."""
        return self.current_usage / self.config.max_tokens
    
    @property
    def status(self) -> BudgetStatus:
        """Get current budget status."""
        ratio = self.usage_ratio
        if ratio >= 1.0:
            return BudgetStatus.EXCEEDED
        if ratio >= self.config.warning_threshold:
            return BudgetStatus.WARNING
        return BudgetStatus.OK
    
    def reset(self):
        """Reset budget usage."""
        self.current_usage = 0
