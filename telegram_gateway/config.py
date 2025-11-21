from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Configuration for the Telegram gateway service."""

    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    backend_base_url: str = Field("http://localhost:8000", env="BACKEND_BASE_URL")
    request_timeout_seconds: float = Field(15.0, env="GATEWAY_REQUEST_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


settings = get_settings()
