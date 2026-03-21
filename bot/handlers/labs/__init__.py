"""Handler for /labs command."""


def handle_labs() -> str:
    """Handle the /labs command.

    Returns:
        List of available labs message.
    """
    return "📋 Доступные лабораторные работы:\n\n- lab-04: Введение в разработку\n- lab-05: Тестирование\n- lab-06: Интеграция\n- lab-07: Деплой\n\nИспользуйте /scores <lab_id> для просмотра оценок."
