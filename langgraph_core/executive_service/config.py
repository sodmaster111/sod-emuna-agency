"""Configuration for the executive LangGraph service."""
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Environment configuration values."""

    LANGGRAPH_EXEC_PORT: int = 8100
    MODEL_URL: str = "http://ollama:11434"
    MODEL_NAME: str = "llama3:8b-instruct"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
