"""Handler for /help command."""


def handle_help() -> str:
    """Handle the /help command.
    
    Returns:
        Help message with available commands.
    """
    return """📚 Доступные команды:

/start - Запустить бота
/help - Показать эту справку
/health - Проверить статус backend
/labs - Показать доступные лабораторные работы
/scores <lab_id> - Показать оценки за лабораторную работу

Вы также можете задавать вопросы естественным языком, например:
- "Какие лабораторные работы доступны?"
- "Покажи мои оценки за lab-04\""""
