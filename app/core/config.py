"""Application configuration management using Pydantic settings."""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./app.db"
DEFAULT_REDIS_URL = "redis://redis:6379/0"
DEFAULT_ENVIRONMENT = "development"


class Settings(BaseSettings):
    """Core application settings sourced from the environment."""

    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    ENVIRONMENT: Optional[str] = None
    TELEGRAM_GATEWAY_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def model_post_init(self, __context: object) -> None:  # noqa: D401
        """Assign fallbacks and log warnings for missing variables."""

        missing_vars: list[str] = []

        if not self.DATABASE_URL:
            missing_vars.append("DATABASE_URL")
            object.__setattr__(self, "DATABASE_URL", DEFAULT_DATABASE_URL)

        if not self.REDIS_URL:
            missing_vars.append("REDIS_URL")
            object.__setattr__(self, "REDIS_URL", DEFAULT_REDIS_URL)

        if not self.ENVIRONMENT:
            missing_vars.append("ENVIRONMENT")
            object.__setattr__(self, "ENVIRONMENT", DEFAULT_ENVIRONMENT)

        if not self.TELEGRAM_GATEWAY_URL:
            missing_vars.append("TELEGRAM_GATEWAY_URL")
            object.__setattr__(self, "TELEGRAM_GATEWAY_URL", "http://telegram-gateway/send-message")

        if missing_vars:
            logger.warning(
                "Missing environment variables for settings: %s. Using default values.",
                ", ".join(missing_vars),
            )

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL or DEFAULT_DATABASE_URL

    @property
    def redis_url(self) -> str:
        return self.REDIS_URL or DEFAULT_REDIS_URL

    @property
    def environment(self) -> str:
        return self.ENVIRONMENT or DEFAULT_ENVIRONMENT

    @property
    def telegram_gateway_url(self) -> str:
        return self.TELEGRAM_GATEWAY_URL or "http://telegram-gateway/send-message"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
