"""TokenCUNT core module."""

# API
from tokencunt.core.api_client import MiniMaxApiClient, ApiResponse
from tokencunt.core.exceptions import (
    TokenCUNTApiError,
    TokenCUNTAuthError,
    TokenCUNTRateLimitError,
    TokenCUNTClientError,
    TokenCUNTTimeoutError,
)

# Token counting
from tokencunt.core.token_counter import TokenCounter, TokenUsage

# Session and budget
from tokencunt.core.session import Session, SessionManager, RequestRecord
from tokencunt.core.budget import BudgetManager, BudgetStatus, BudgetConfig

# Batcher and optimizer
from tokencunt.core.batcher import RequestBatcher, BatchedRequest
from tokencunt.core.optimizer import PromptOptimizer

__all__ = [
    # API
    "MiniMaxApiClient",
    "ApiResponse",
    "TokenCUNTApiError",
    "TokenCUNTAuthError", 
    "TokenCUNTRateLimitError",
    "TokenCUNTClientError",
    "TokenCUNTTimeoutError",
    # Token
    "TokenCounter",
    "TokenUsage",
    # Session
    "Session",
    "SessionManager",
    "RequestRecord",
    # Budget
    "BudgetManager",
    "BudgetStatus",
    "BudgetConfig",
    # Batcher
    "RequestBatcher",
    "BatchedRequest",
    # Optimizer
    "PromptOptimizer",
]
