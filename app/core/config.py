from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}/{self.postgres_db}"
        )


settings = Settings()
