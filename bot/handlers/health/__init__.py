"""Handler for /health command."""

from services.lms_client import HealthStatus


def handle_health(status: HealthStatus) -> str:
    """Handle the /health command.

    Args:
        status: The health status from the LMS client.

    Returns:
        Backend health status message.
    """
    if status.healthy:
        return f"✅ Backend доступен и работает нормально. Доступно элементов: {status.item_count}"
    else:
        return f"❌ Backend error: {status.error}"
