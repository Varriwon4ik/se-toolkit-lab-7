"""Handler for /labs command."""


def handle_labs(labs: list[dict], error: str | None = None) -> str:
    """Handle the /labs command.

    Args:
        labs: List of lab dictionaries from the LMS API.
        error: Error message if the API call failed.

    Returns:
        List of available labs message.
    """
    if error:
        return f"❌ Backend error: {error}"

    if not labs:
        return "📋 Нет доступных лабораторных работ."

    lines = ["📋 Доступные лабораторные работы:"]
    for lab in labs:
        title = lab.get("title", lab.get("name", "Unknown"))
        lines.append(f"- {title}")

    return "\n".join(lines)
