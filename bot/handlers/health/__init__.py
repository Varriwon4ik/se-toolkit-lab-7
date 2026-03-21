"""Handler for /health command."""


def handle_health() -> str:
    """Handle the /health command.

    Returns:
        Backend health status message.
    """
    return "✅ Backend доступен и работает нормально."
