"""Application configuration utilities."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AppConfig:
    """Centralized configuration for the Digital Sanhedrin."""

    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2"))

    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://redis:6379/0"))
    postgres_url: str = field(
        default_factory=lambda: os.getenv(
            "POSTGRES_URL",
            "postgresql+psycopg://postgres:postgres@postgres:5432/sanhedrin",
        )
    )

    temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.3")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "4096")))

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


config = AppConfig()
