from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or defaults."""

    PROJECT_NAME: str = "Gocompliances CRM API"
    ADMIN_PROJECT_NAME: str = "Gocompliances Database Admin"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # Server settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ADMIN_PORT: int = 8001

    # Routing prefixes
    API_PREFIX: str = "/api"

    # Frontend and CORS settings
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    ADMIN_FRONTEND_ORIGIN: str = "http://localhost:8001"
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:5173", "http://localhost:8001"]

    # Database settings
    DATABASE_URL: str = ""
    DB_POOL_PRE_PING: bool = True
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_CONNECT_TIMEOUT: int = 5

    # JWT Authentication & Security settings
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCK_MINUTES: int = 15

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "DATABASE_URL is not configured. Please define DATABASE_URL in your .env file or environment."
            )
        url = v.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "JWT_SECRET_KEY is not configured. Please define JWT_SECRET_KEY in your .env file or environment."
            )
        secret = v.strip()
        if len(secret) < 32:
            raise ValueError(
                "JWT_SECRET_KEY is too short. It must be at least 32 characters long for security."
            )
        return secret

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return [str(v)]

    @property
    def masked_database_url(self) -> str:
        """Return DATABASE_URL with password masked for safe logging/display."""
        if not self.DATABASE_URL:
            return ""
        try:
            from sqlalchemy.engine.url import make_url
            url = make_url(self.DATABASE_URL)
            return url.render_as_string(hide_password=True)
        except Exception:
            return "postgresql+psycopg://***"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
