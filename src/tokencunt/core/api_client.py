"""MiniMax API client with retry logic."""

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from typing import Optional, Any
import asyncio

from tokencunt.core.exceptions import (
    TokenCUNTApiError,
    TokenCUNTAuthError,
    TokenCUNTRateLimitError,
    TokenCUNTClientError,
    TokenCUNTTimeoutError,
)


class ApiResponse:
    """Parsed API response."""
    
    def __init__(
        self,
        content: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        response_id: str,
        raw_response: dict = None
    ):
        self.content = content
        self.model = model
        self.usage = UsageInfo(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens
        )
        self.id = response_id
        self._raw = raw_response or {}
    
    @property
    def total_tokens(self) -> int:
        return self.usage.prompt_tokens + self.usage.completion_tokens


class UsageInfo:
    """Token usage information."""
    
    def __init__(self, prompt_tokens: int = 0, completion_tokens: int = 0):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
    
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class MiniMaxApiClient:
    """MiniMax API client with automatic retry on transient failures."""
    
    def __init__(
        self,
        api_key: str,
        group_id: str,
        model: str = "MiniMax-M2.5",
        base_url: str = "https://api.minimax.io/v1",
        timeout: float = 60.0
    ):
        """
        Initialize the API client.
        
        Args:
            api_key: MiniMax API key
            group_id: MiniMax group ID
            model: Model to use (default: MiniMax-M2.5)
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.group_id = group_id
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    async def chat(
        self,
        messages: list[dict],
        **kwargs
    ) -> ApiResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            ApiResponse with content, usage, model, and id
        """
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            **kwargs
        }
        
        return await self._make_request(
            endpoint="/text/chatcompletion_v2",
            payload=payload
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((
            httpx.HTTPError,
            httpx.TimeoutException,
            TokenCUNTRateLimitError,
        ))
    )
    async def _make_request(
        self,
        endpoint: str,
        payload: dict
    ) -> ApiResponse:
        """
        Make API request with retry logic.
        
        Args:
            endpoint: API endpoint path
            payload: Request payload
        
        Returns:
            ApiResponse object
        """
        client = await self._get_client()
        
        url = f"/{self.group_id}{endpoint}"
        
        try:
            response = await client.post(url, json=payload)
            return self._parse_response(response)
        except httpx.TimeoutException as e:
            raise TokenCUNTTimeoutError(
                f"Request timed out after {self.timeout}s",
                suggested_fix="Try again with a longer timeout"
            ) from e
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
    
    def _parse_response(self, response: httpx.Response) -> ApiResponse:
        """Parse API response into ApiResponse object."""
        if response.status_code != 200:
            self._handle_http_error(response)
        
        data = response.json()
        
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        usage_data = data.get("usage", {})
        
        return ApiResponse(
            content=message.get("content", ""),
            model=data.get("model", self.model),
            input_tokens=usage_data.get("prompt_tokens", 0),
            output_tokens=usage_data.get("completion_tokens", 0),
            response_id=data.get("id", ""),
            raw_response=data
        )
    
    def _handle_http_error(self, response: httpx.Response):
        """Convert HTTP error to appropriate TokenCUNT exception."""
        status = response.status_code
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", response.text)
        except Exception:
            error_msg = response.text
        
        if status == 401:
            raise TokenCUNTAuthError(error_msg, status=status)
        elif status == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            raise TokenCUNTRateLimitError(
                f"{error_msg} (retry after: {retry_after}s)",
                status=status
            )
        elif 400 <= status < 500:
            raise TokenCUNTClientError(error_msg, status=status)
        elif status >= 500:
            raise TokenCUNTApiError(
                f"Server error: {error_msg}",
                status=status,
                suggested_fix="This is a server-side issue. Try again later."
            )
        else:
            raise TokenCUNTApiError(error_msg, status=status)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
