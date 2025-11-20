"""Application settings and environment configuration."""
from __future__ import annotations

from functools import lru_cache

try:  # Pydantic v2 ships BaseSettings in a separate package
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:  # pragma: no cover - fallback for environments pinned to v1
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Centralized runtime configuration for the backend."""

    database_url: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        description="SQLAlchemy-compatible database URL",
        env="DATABASE_URL",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URI for Celery and caching",
        env="REDIS_URL",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for the Ollama-compatible litellm proxy",
        env="OLLAMA_BASE_URL",
    )
    mission_goal: str = Field(
        default=(
            "Grow the Digital Sanhedrin's assets while remaining halachically and"
            " ethically compliant."
        ),
        description="Primary mission objective for the council",
        env="MISSION_GOAL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
