from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:U566V9c1ZuHuQcWBfyOEPoSz4dzrMzUT2vxHvR8jTatx7iAqGkj1pK6utomOjJE5@postgresql-database-j4ss4c0g8ss4wwoc444k4gwo:5432/postgres"
    )

    # Redis
    REDIS_URL: str = "redis://redis-database-msgk84o0k800ogw8coc4s4sg:6379/0"

    # Ollama LLM
    OLLAMA_BASE_URL: str = "http://ollama-with-open-webui-e0gw40o8884c04sskkg4wcww:11434/v1"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # External APIs
    SEFARIA_API_URL: str = "https://www.sefaria.org/api"
    HEBCAL_API_URL: str = "https://www.hebcal.com/shabbat"

    # TON Wallet
    TON_WALLET_ADDRESS: str = "UQC_uDgg1EDFSwK_SfdEnevfPsfKIs1HhTKrPwS8QXYDG8my"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Mission
    MISSION_GOAL: str = "Generate 1,000,000 TON profit using ethical marketing and NFT sales"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
