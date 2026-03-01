"""Custom exception classes for TokenCUNT."""

from typing import Optional


class TokenCUNTApiError(Exception):
    """Base exception for TokenCUNT API errors."""
    
    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        suggested_fix: Optional[str] = None
    ):
        self.message = message
        self.status = status
        self.suggested_fix = suggested_fix
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        parts = [self.message]
        if self.status is not None:
            parts.append(f"status: {self.status}")
        if self.suggested_fix:
            parts.append(f"suggested fix: {self.suggested_fix}")
        return f"{self.__class__.__name__}: {' | '.join(parts)}"


class TokenCUNTAuthError(TokenCUNTApiError):
    """Authentication error (401)."""
    
    def __init__(self, message: str = "Authentication failed", status: int = 401, **kwargs):
        kwargs.setdefault("suggested_fix", "Check your MINIMAX_API_KEY and GROUP_ID environment variables")
        super().__init__(message, status, **kwargs)


class TokenCUNTRateLimitError(TokenCUNTApiError):
    """Rate limit error (429)."""
    
    def __init__(self, message: str = "Rate limit exceeded", status: int = 429, suggested_fix: Optional[str] = None, **kwargs):
        kwargs.setdefault("suggested_fix", "Wait before retrying or implement request batching")
        super().__init__(message, status, **kwargs)


class TokenCUNTClientError(TokenCUNTApiError):
    """Client error (4xx except 401)."""
    
    def __init__(self, message: str = "Client error", status: Optional[int] = None, suggested_fix: Optional[str] = None, **kwargs):
        kwargs.setdefault("suggested_fix", "Check your request format and parameters")
        super().__init__(message, status, **kwargs)


class TokenCUNTTimeoutError(TokenCUNTApiError):
    """Timeout error."""
    
    def __init__(self, message: str = "Request timed out", status: Optional[int] = None, suggested_fix: Optional[str] = None, **kwargs):
        kwargs.setdefault("suggested_fix", "Try again with a longer timeout or check your network")
        super().__init__(message, status, **kwargs)
