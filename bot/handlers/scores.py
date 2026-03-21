"""Handler for /scores command."""

from services.lms_client import PassRate


def handle_scores(lab_id: str | None = None, pass_rates: list[PassRate] | None = None, error: str | None = None) -> str:
    """Handle the /scores command.

    Args:
        lab_id: The lab identifier (e.g., "lab-04").
        pass_rates: List of pass rates from the LMS API.
        error: Error message if the API call failed.

    Returns:
        Scores information message.
    """
    if lab_id is None:
        return "❌ Пожалуйста, укажите ID лабораторной работы.\n\nПример: /scores lab-04"

    if error:
        return f"❌ Backend error: {error}"

    if pass_rates is None or not pass_rates:
        return f"📊 Нет данных об оценках для {lab_id}."

    lines = [f"📊 Оценки за {lab_id}:"]
    for pr in pass_rates:
        percentage = pr.pass_rate * 100 if pr.pass_rate <= 1 else pr.pass_rate
        lines.append(f"- {pr.task_name}: {percentage:.1f}% ({pr.attempts} попыток)")

    return "\n".join(lines)
