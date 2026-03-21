"""LMS API client."""

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class HealthStatus:
    """Health check result."""

    healthy: bool
    item_count: int | None = None
    error: str | None = None


@dataclass
class PassRate:
    """Pass rate for a task."""

    task_name: str
    pass_rate: float
    attempts: int


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

    def _format_error(self, exc: Exception) -> str:
        """Format an exception into a user-friendly error message.

        Args:
            exc: The exception to format.

        Returns:
            A user-friendly error message.
        """
        if isinstance(exc, httpx.ConnectError):
            return f"connection refused ({self.base_url}). Check that the services are running."
        elif isinstance(exc, httpx.HTTPStatusError):
            return f"HTTP {exc.response.status_code} {exc.response.reason_phrase}. The backend service may be down."
        elif isinstance(exc, httpx.TimeoutException):
            return f"timeout connecting to {self.base_url}. The backend is taking too long to respond."
        elif isinstance(exc, httpx.HTTPError):
            return f"HTTP error: {str(exc)}"
        else:
            return f"unexpected error: {str(exc)}"

    async def health_check(self) -> HealthStatus:
        """Check if the LMS backend is available.

        Returns:
            HealthStatus with health information.
        """
        try:
            client = await self._get_client()
            response = await client.get("/items")
            response.raise_for_status()
            items = response.json()
            item_count = len(items) if isinstance(items, list) else 0
            return HealthStatus(healthy=True, item_count=item_count)
        except Exception as exc:
            return HealthStatus(healthy=False, error=self._format_error(exc))

    async def get_labs(self) -> tuple[list[dict], str | None]:
        """Get the list of available labs.

        Returns:
            Tuple of (list of lab dictionaries, error message or None).
        """
        try:
            client = await self._get_client()
            response = await client.get("/items")
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data, None
            return [], None
        except Exception as exc:
            return [], self._format_error(exc)

    async def get_pass_rates(self, lab_id: str) -> tuple[list[PassRate], str | None]:
        """Get pass rates for a specific lab.

        Args:
            lab_id: The lab identifier.

        Returns:
            Tuple of (list of PassRate objects, error message or None).
        """
        try:
            client = await self._get_client()
            response = await client.get(
                "/analytics/pass-rates",
                params={"lab": lab_id},
            )
            response.raise_for_status()
            data = response.json()

            pass_rates = []
            if isinstance(data, list):
                for item in data:
                    task_name = item.get("task_name", item.get("task", "Unknown"))
                    pass_rate = item.get("pass_rate", item.get("average", 0))
                    attempts = item.get("attempts", item.get("count", 0))
                    pass_rates.append(
                        PassRate(
                            task_name=task_name,
                            pass_rate=pass_rate,
                            attempts=attempts,
                        )
                    )
            return pass_rates, None
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return [], f"lab {lab_id} not found"
            return [], self._format_error(exc)
        except Exception as exc:
            return [], self._format_error(exc)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
