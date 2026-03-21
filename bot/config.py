"""Configuration loading for the LMS Telegram Bot."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this config.py file is located (bot/)
# The .env.bot.secret file is in the project root (parent of bot/)
BOT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BOT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    # Telegram
    bot_token: str = Field(default="", alias="BOT_TOKEN")

    # LMS API
    lms_api_base_url: str = Field(default="", alias="LMS_API_BASE_URL")
    lms_api_key: str = Field(default="", alias="LMS_API_KEY")

    # LLM API
    llm_api_base_url: str = Field(default="", alias="LLM_API_BASE_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_api_model: str = Field(default="coder-model", alias="LLM_API_MODEL")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = BotSettings.model_validate({})
