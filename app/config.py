"""Application configuration."""

import secrets
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///./job_board.db"

    # Server
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8000
    MCP_SERVER_NAME: str = "Mackay Job Board MCP"
    DEBUG: bool = True

    # Authentication
    ENABLE_AUTH: bool = False
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Job Board
    DEFAULT_LOCATION: str = "Mackay"
    ENABLE_SEED_DATA: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL.lower()

    @property
    def database_path(self) -> Optional[Path]:
        if self.is_sqlite:
            path = self.DATABASE_URL.replace("sqlite:///", "")
            return Path(path)
        return None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
