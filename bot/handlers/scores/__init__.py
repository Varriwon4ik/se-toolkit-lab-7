"""Handler for /scores command."""


def handle_scores(lab_id: str | None = None) -> str:
    """Handle the /scores command.

    Args:
        lab_id: The lab identifier (e.g., "lab-04").

    Returns:
        Scores information message.
    """
    if lab_id is None:
        return "❌ Пожалуйста, укажите ID лабораторной работы.\n\nПример: /scores lab-04"

    return f"📊 Оценки за {lab_id}:\n\nСтатус: Проверено\nБаллы: 10/10\n\n(Данные будут загружены из LMS API в следующей версии)"
