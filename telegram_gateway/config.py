from __future__ import annotations

import json
from typing import Dict, Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Configuration for the Telegram gateway service."""

    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    backend_base_url: str = Field("http://localhost:8000", env="BACKEND_BASE_URL")
    request_timeout_seconds: float = Field(15.0, env="GATEWAY_REQUEST_TIMEOUT")
    channels_map: Optional[Dict[str, int]] = Field(default=None, env="CHANNELS_MAP")

    @validator("channels_map", pre=True)
    def _parse_channels_map(cls, value: object) -> Optional[Dict[str, int]]:
        """Parse CHANNELS_MAP env var supplied as JSON string."""

        if value is None or isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("CHANNELS_MAP must be valid JSON") from exc
            if parsed is None:
                return None
            if not isinstance(parsed, dict):
                raise ValueError("CHANNELS_MAP must decode to a mapping")
            return parsed
        raise TypeError("CHANNELS_MAP must be a dict or JSON string")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


settings = get_settings()
