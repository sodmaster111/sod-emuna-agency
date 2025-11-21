"""Configuration for the WhatsApp gateway service."""
from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Environment-backed settings for the WhatsApp gateway."""

    wa_provider: str = Field(..., alias="WA_PROVIDER", description="Provider identifier: cloud_api or twilio")
    wa_api_base_url: str = Field(..., alias="WA_API_BASE_URL", description="Base URL for the WhatsApp provider API")
    wa_api_token: str = Field(..., alias="WA_API_TOKEN", description="Authentication token for the provider")
    wa_default_from: str = Field(..., alias="WA_DEFAULT_FROM", description="Default sender phone number or ID")

    class Config:
        case_sensitive = False
        env_file = ".env"
        allow_population_by_field_name = True


def get_settings() -> Settings:
    """Return cached settings instance."""

    @lru_cache()
    def _cached() -> Settings:
        return Settings()

    return _cached()
