"""LLM API client for intent routing."""

import httpx


class LLMClient:
    """Client for the LLM API."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """Initialize the LLM client.
        
        Args:
            base_url: The LLM API base URL.
            api_key: The LLM API authentication key.
            model: The model name to use.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=60.0,
            )
        return self._client

    async def route_intent(self, message: str) -> str:
        """Route a user message to the appropriate command.
        
        Args:
            message: The user's message text.
            
        Returns:
            The command to execute (e.g., "/labs", "/scores lab-04").
        """
        # Placeholder implementation - will be enhanced in Task 3
        return "/help"

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
