from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    DATABASE_URL: str = "postgresql+asyncpg://postgres:sodpassword@postgresql:5432/sod_db"
    REDIS_URL: str = "redis://redis:6379/0"
    OLLAMA_BASE_URL: str = "http://ollama:11434/v1"
    OLLAMA_MODEL: str = "llama3.1:8b"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG_SQL: bool = False

    @property
    def redis_url(self) -> str:
        return self.REDIS_URL

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def ollama_base_url(self) -> str:
        return self.OLLAMA_BASE_URL

    @property
    def ollama_model(self) -> str:
        return self.OLLAMA_MODEL

    @property
    def host(self) -> str:
        return self.HOST

    @property
    def port(self) -> int:
        return self.PORT

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
