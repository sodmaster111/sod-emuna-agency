"""Application settings and environment configuration for core services."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized runtime configuration for backend services."""

    database_url: str = Field(
        default=(
            "postgresql://postgres:U566V9c1ZuHuQcWBfyOEPoSz4dzrMzUT2vxHvR8jTatx7iAqGkj1pK6utomOjJE5"
            "@postgresql-database-j4ss4c0g8ss4wwoc444k4gwo:5432/postgres"
        ),
        description="SQLAlchemy/asyncpg-compatible database URL",
        env="DATABASE_URL",
    )
    redis_url: str = Field(
        default="redis://redis-database-msgk84o0k800ogw8coc4s4sg:6379",
        description="Redis connection URI for Celery and caching",
        env="REDIS_URL",
    )
    ollama_base_url: str = Field(
        default="http://ollama-with-open-webui-e0gw40o8884c04sskkg4wcww:11434/v1",
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


config = get_settings()

__all__ = ["Settings", "get_settings", "config"]
