"""Application configuration utilities using Pydantic settings."""
from __future__ import annotations

from typing import Any, Dict

import litellm
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Centralized configuration for the Digital Sanhedrin services."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core service URLs
    postgres_url: str = (
        "postgresql://postgres:U566V9c1ZuHuQcWBfyOEPoSz4dzrMzUT2vxHvR8jTatx7iAqGkj1pK6utomOjJE5"
        "@postgresql-database-j4ss4c0g8ss4wwoc444k4gwo:5432/postgres"
    )
    redis_url: str = "redis://redis-database-msgk84o0k800ogw8coc4s4sg:6379"
    ollama_base_url: str = "http://ollama-with-open-webui-e0gw40o8884c04sskkg4wcww:11434/v1"

    # LLM defaults
    ollama_model: str = "llama3.2"
    temperature: float = 0.3
    max_tokens: int = 4096

    @property
    def async_postgres_url(self) -> str:
        """Return the asyncpg connection string for SQLAlchemy."""

        if self.postgres_url.startswith("postgresql+asyncpg"):
            return self.postgres_url
        if self.postgres_url.startswith("postgres://"):
            return self.postgres_url.replace("postgres://", "postgresql+asyncpg://", 1)
        return self.postgres_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def llm_config(self) -> Dict[str, Any]:
        """LiteLLM configuration used by AutoGen agents."""

        return {
            "model": self.ollama_model,
            "api_base": self.ollama_base_url,
            "api_type": "ollama",
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def configure_litellm(self) -> None:
        """Configure global LiteLLM defaults for Ollama."""

        litellm.api_base = self.ollama_base_url
        litellm.model = self.ollama_model


def load_config() -> AppConfig:
    """Initialize the application configuration and wire LiteLLM."""

    cfg = AppConfig()
    cfg.configure_litellm()
    return cfg


config = load_config()
