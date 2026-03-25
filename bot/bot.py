"""LMS Telegram Bot entry point."""

import argparse
import asyncio
import sys
from typing import NoReturn

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import settings
from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)
from services import LLMClient, LMSClient

# Global service clients for use in handlers
_lms_client: LMSClient | None = None
_llm_client: LLMClient | None = None


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the specified command (e.g., '/start')",
    )
    return parser.parse_args()


def parse_command(command: str) -> tuple[str, str | None]:
    """Parse a command string into command and arguments.

    Args:
        command: The command string (e.g., '/scores lab-04').

    Returns:
        Tuple of (command_name, argument).
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None
    return cmd, arg


async def get_handler_response(
    command: str,
    arg: str | None,
    lms_client: LMSClient,
) -> str:
    """Get response from the appropriate handler.

    Args:
        command: The command name (e.g., '/start').
        arg: Optional command argument.
        lms_client: The LMS API client.

    Returns:
        Response text from the handler.
    """
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        status = await lms_client.health_check()
        return handle_health(status)
    elif command == "/labs":
        labs, error = await lms_client.get_labs()
        return handle_labs(labs, error)
    elif command == "/scores":
        if arg is None:
            return handle_scores(lab_id=None)
        pass_rates, error = await lms_client.get_pass_rates(arg)
        return handle_scores(lab_id=arg, pass_rates=pass_rates, error=error)
    else:
        return "❌ Неизвестная команда. Используйте /help для просмотра доступных команд."


async def run_test_mode(command: str) -> NoReturn:
    """Run the bot in test mode.

    Args:
        command: The command to test (e.g., '/start').
    """
    cmd, arg = parse_command(command)

    # Initialize LMS client for API calls
    lms_client = LMSClient(settings.lms_api_base_url, settings.lms_api_key)

    # Initialize LLM client for natural language routing
    llm_client = LLMClient(
        settings.llm_api_base_url, settings.llm_api_key, settings.llm_api_model
    )
    llm_client.set_lms_client(lms_client)

    try:
        # Check if it's a natural language query (not a slash command)
        if cmd.startswith("/"):
            response = await get_handler_response(cmd, arg, lms_client)
        else:
            response = await llm_client.route_intent(command)
    finally:
        await lms_client.close()
        await llm_client.close()

    print(response)
    sys.exit(0)


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for /start command.

    Returns:
        InlineKeyboardMarkup with common action buttons.
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📋 Доступные лабы", callback_data="action_labs"),
            InlineKeyboardButton(text="💚 Health", callback_data="action_health"),
        ],
        [
            InlineKeyboardButton(text="📊 Оценки (lab-04)", callback_data="action_scores_lab-04"),
            InlineKeyboardButton(text="👥 Топ студентов", callback_data="action_top_lab-04"),
        ],
        [
            InlineKeyboardButton(text="❓ Помощь", callback_data="action_help"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def handle_start_command(message: types.Message) -> None:
    """Handle /start command from Telegram."""
    response = handle_start()
    keyboard = get_start_keyboard()
    await message.answer(response, reply_markup=keyboard)


async def handle_help_command(message: types.Message) -> None:
    """Handle /help command from Telegram."""
    response = handle_help()
    await message.answer(response)


async def handle_health_command(message: types.Message) -> None:
    """Handle /health command from Telegram."""
    if _lms_client is None:
        await message.answer("❌ Bot not initialized properly")
        return
    status = await _lms_client.health_check()
    response = handle_health(status)
    await message.answer(response)


async def handle_labs_command(message: types.Message) -> None:
    """Handle /labs command from Telegram."""
    if _lms_client is None:
        await message.answer("❌ Bot not initialized properly")
        return
    labs, error = await _lms_client.get_labs()
    response = handle_labs(labs, error)
    await message.answer(response)


async def handle_scores_command(message: types.Message) -> None:
    """Handle /scores command from Telegram.

    Args:
        message: The Telegram message.
    """
    if _lms_client is None:
        await message.answer("❌ Bot not initialized properly")
        return

    args = message.text.split()[1:] if message.text else []
    lab_id = args[0] if args else None

    if lab_id is None:
        response = handle_scores(lab_id=None)
    else:
        pass_rates, error = await _lms_client.get_pass_rates(lab_id)
        response = handle_scores(lab_id=lab_id, pass_rates=pass_rates, error=error)

    await message.answer(response)


async def handle_message(message: types.Message) -> None:
    """Handle regular messages using LLM for intent routing.

    Args:
        message: The Telegram message.
    """
    if _llm_client is None:
        await message.answer("❌ Bot not initialized properly")
        return

    user_text = message.text or ""
    response = await _llm_client.route_intent(user_text)
    await message.answer(response)


async def handle_callback_query(callback_query: types.CallbackQuery) -> None:
    """Handle inline keyboard button callbacks.

    Args:
        callback_query: The callback query from Telegram.
    """
    action = callback_query.data
    response = ""

    if action == "action_labs":
        if _lms_client is None:
            response = "❌ Bot not initialized properly"
        else:
            labs, error = await _lms_client.get_labs()
            response = handle_labs(labs, error)

    elif action == "action_health":
        if _lms_client is None:
            response = "❌ Bot not initialized properly"
        else:
            status = await _lms_client.health_check()
            response = handle_health(status)

    elif action == "action_scores_lab-04":
        if _lms_client is None:
            response = "❌ Bot not initialized properly"
        else:
            pass_rates, error = await _lms_client.get_pass_rates("lab-04")
            response = handle_scores(lab_id="lab-04", pass_rates=pass_rates, error=error)

    elif action == "action_top_lab-04":
        if _lms_client is None:
            response = "❌ Bot not initialized properly"
        else:
            client = await _lms_client._get_client()
            try:
                resp = await client.get("/analytics/top-learners", params={"lab": "lab-04", "limit": 5})
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list) and data:
                    lines = ["👥 Топ студентов в Lab 04:"]
                    for i, learner in enumerate(data[:5], 1):
                        name = learner.get("name", learner.get("learner_name", "Unknown"))
                        score = learner.get("score", learner.get("average", 0))
                        lines.append(f"{i}. {name}: {score:.1f}%")
                    response = "\n".join(lines)
                else:
                    response = "📊 Нет данных о топ студентах для lab-04."
            except Exception as exc:
                response = f"❌ Error: {str(exc)}"

    elif action == "action_help":
        response = handle_help()

    else:
        response = "❓ Неизвестное действие"

    await callback_query.message.answer(response)
    await callback_query.answer()


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode."""
    global _lms_client, _llm_client

    if not settings.bot_token:
        print("Ошибка: BOT_TOKEN не указан в .env.bot.secret", file=sys.stderr)
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()

    # Initialize service clients
    _lms_client = LMSClient(settings.lms_api_base_url, settings.lms_api_key)
    _llm_client = LLMClient(
        settings.llm_api_base_url, settings.llm_api_key, settings.llm_api_model
    )
    _llm_client.set_lms_client(_lms_client)

    # Register command handlers
    dispatcher.message.register(handle_start_command, CommandStart())
    dispatcher.message.register(handle_help_command, Command("help"))
    dispatcher.message.register(handle_health_command, Command("health"))
    dispatcher.message.register(handle_labs_command, Command("labs"))
    dispatcher.message.register(handle_scores_command, Command("scores"))
    dispatcher.message.register(handle_message)

    # Register callback query handler for inline buttons
    dispatcher.callback_query.register(handle_callback_query)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        if _lms_client:
            await _lms_client.close()
        if _llm_client:
            await _llm_client.close()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.test:
        asyncio.run(run_test_mode(args.test))
    else:
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
