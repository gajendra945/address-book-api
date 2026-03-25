from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Address Book API"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = Field(default=8000, ge=1, le=65535)
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./address_book.db"
    DEFAULT_PAGE_LIMIT: int = Field(default=20, ge=1, le=1000)
    MAX_PAGE_LIMIT: int = Field(default=100, ge=1, le=1000)

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on", "debug"}
        return bool(value)

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def normalize_log_level(cls, value: object) -> str:
        return str(value).upper()

    @field_validator("API_V1_PREFIX", mode="before")
    @classmethod
    def normalize_api_prefix(cls, value: object) -> str:
        prefix = str(value).strip() or "/api/v1"
        prefix = prefix if prefix.startswith("/") else f"/{prefix}"
        return prefix.rstrip("/") or "/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
