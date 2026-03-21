"""LMS API client."""

import httpx


class LMSClient:
    """Client for the LMS API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the LMS client.
        
        Args:
            base_url: The LMS API base URL.
            api_key: The LMS API authentication key.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0,
            )
        return self._client

    async def health_check(self) -> bool:
        """Check if the LMS backend is available.
        
        Returns:
            True if the backend is healthy, False otherwise.
        """
        try:
            client = await self._get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def get_labs(self) -> list[dict]:
        """Get the list of available labs.
        
        Returns:
            List of lab dictionaries.
        """
        try:
            client = await self._get_client()
            response = await client.get("/items")
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    async def get_scores(self, lab_id: str) -> dict | None:
        """Get scores for a specific lab.
        
        Args:
            lab_id: The lab identifier.
            
        Returns:
            Scores dictionary or None if not found.
        """
        try:
            client = await self._get_client()
            response = await client.get(f"/analytics/{lab_id}")
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
