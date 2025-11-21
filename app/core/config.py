from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment with secure defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    database_url: str = Field(
        default=(
            "postgresql://postgres:U566V9c1ZuHuQcWBfyOEPoSz4dzrMzUT2vxHvR8jTatx7iAqGkj1pK6utomOjJE5"
            "@postgresql-database-j4ss4c0g8ss4wwoc444k4gwo:5432/postgres"
        ),
        env="DATABASE_URL",
        description="SQLAlchemy async database URL",
    )
    redis_url: str = Field(
        default="redis://redis-database-msgk84o0k800ogw8coc4s4sg:6379",
        env="REDIS_URL",
        description="Redis connection string for Celery and cache",
    )
    ollama_base_url: str = Field(
        default="http://ollama-with-open-webui-e0gw40o8884c04sskkg4wcww:11434/v1",
        env="OLLAMA_BASE_URL",
        description="Base URL for the Ollama-compatible endpoint",
    )
    ton_wallet_address: str = Field(
        default="UQC_uDgg1EDFSwK_SfdEnevfPsfKIs1HhTKrPwS8QXYDG8my",
        env="TON_WALLET_ADDRESS",
        description="Treasury TON wallet address",
    )
    mission_goal: str = Field(
        default="Generate 1,000,000 TON profit using ethical marketing and NFT sales.",
        env="MISSION_GOAL",
        description="Primary mission objective",
    )
    ton_wallet_address: str = Field(
        default="",
        description="TON wallet address used for treasury status checks",
        env="TON_WALLET_ADDRESS",
    )

    langfuse_secret_key: str = Field(
        default="",
        description="Secret key for authenticating with Langfuse",
        env="LANGFUSE_SECRET_KEY",
    )
    langfuse_public_key: str = Field(
        default="",
        description="Public key for authenticating with Langfuse",
        env="LANGFUSE_PUBLIC_KEY",
    )
    langfuse_host: str = Field(
        default="https://trace.sodmaster.online",
        description="Base URL for Langfuse tracing backend",
        env="LANGFUSE_HOST",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()

settings = Settings()
