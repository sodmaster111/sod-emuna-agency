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
    ollama_model: str = Field(
        default="gpt-4o-mini",
        description="Model identifier served by the Ollama-compatible endpoint",
        env="OLLAMA_MODEL",
    )
    temperature: float = Field(
        default=0.2,
        description="Default sampling temperature for LLM calls",
        env="OLLAMA_TEMPERATURE",
    )
    max_tokens: int = Field(
        default=2048,
        description="Token budget for generation where applicable",
        env="OLLAMA_MAX_TOKENS",
    )
    mission_goal: str = Field(
        default=(
            "Grow the Digital Sanhedrin's assets while remaining halachically and"
            " ethically compliant."
        ),
        description="Primary mission objective for the council",
        env="MISSION_GOAL",
    )
    ton_wallet_address: str = Field(
        default="",
        description="TON wallet address used for treasury status checks",
        env="TON_WALLET_ADDRESS",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]

# Backwards compatibility aliases
AppConfig = Settings
config = get_settings()

__all__ += ["AppConfig", "config"]
