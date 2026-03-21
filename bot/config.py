"""Configuration loading for the LMS Telegram Bot."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = BotSettings.model_validate({})
