from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or defaults."""

    PROJECT_NAME: str = "Gocompliances CRM API"
    ADMIN_PROJECT_NAME: str = "Gocompliances Database Admin"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    APP_ENV: Optional[str] = None

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
    TEST_DATABASE_URL: Optional[str] = None
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

    # Trial Phase Default Password Provisioning (Temporary local trial only)
    TRIAL_DEFAULT_PASSWORD_ENABLED: bool = False
    TRIAL_DEFAULT_PASSWORD: Optional[str] = None

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

    @field_validator("TEST_DATABASE_URL")
    @classmethod
    def validate_test_database_url_format(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
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

    @property
    def is_production(self) -> bool:
        """Return True if application is running in production environment mode."""
        env = (self.APP_ENV or self.ENVIRONMENT or "").strip().lower()
        return env in {"production", "prod"}

    def get_effective_trial_password(self) -> Optional[str]:
        """Return configured trial password if enabled and safe, else raise ValueError."""
        if not self.TRIAL_DEFAULT_PASSWORD_ENABLED:
            return None
        if self.is_production:
            raise ValueError(
                "Trial default password mode is strictly forbidden in production environment."
            )
        if not self.TRIAL_DEFAULT_PASSWORD or not self.TRIAL_DEFAULT_PASSWORD.strip():
            raise ValueError(
                "TRIAL_DEFAULT_PASSWORD_ENABLED is true but TRIAL_DEFAULT_PASSWORD is empty or not configured."
            )
        return self.TRIAL_DEFAULT_PASSWORD.strip()

    @property
    def masked_test_database_url(self) -> str:
        """Return TEST_DATABASE_URL with password masked for safe logging/display."""
        if not self.TEST_DATABASE_URL:
            return ""
        try:
            from sqlalchemy.engine.url import make_url
            url = make_url(self.TEST_DATABASE_URL)
            return url.render_as_string(hide_password=True)
        except Exception:
            return "postgresql+psycopg://***"

    @staticmethod
    def validate_test_database_isolation(test_url: Optional[str], dev_url: str) -> str:
        """Validate that TEST_DATABASE_URL is configured, valid, distinct from dev URL, and points to a dedicated test DB."""
        if not test_url or not test_url.strip():
            raise ValueError(
                "TEST_DATABASE_URL is not configured. Automated tests must not run against the development database."
            )
        test_url_clean = test_url.strip()
        if test_url_clean.startswith("postgres://"):
            test_url_clean = test_url_clean.replace("postgres://", "postgresql+psycopg://", 1)
        elif test_url_clean.startswith("postgresql://") and not test_url_clean.startswith("postgresql+"):
            test_url_clean = test_url_clean.replace("postgresql://", "postgresql+psycopg://", 1)

        dev_url_clean = dev_url.strip() if dev_url else ""
        if dev_url_clean.startswith("postgres://"):
            dev_url_clean = dev_url_clean.replace("postgres://", "postgresql+psycopg://", 1)
        elif dev_url_clean.startswith("postgresql://") and not dev_url_clean.startswith("postgresql+"):
            dev_url_clean = dev_url_clean.replace("postgresql://", "postgresql+psycopg://", 1)

        from sqlalchemy.engine.url import make_url

        try:
            parsed_test = make_url(test_url_clean)
        except Exception:
            raise ValueError("TEST_DATABASE_URL is invalid.")

        try:
            parsed_dev = make_url(dev_url_clean) if dev_url_clean else None
        except Exception:
            parsed_dev = None

        # Check 1: Must not match development database
        if parsed_dev and (
            test_url_clean == dev_url_clean
            or (
                parsed_test.host == parsed_dev.host
                and (parsed_test.port or 5432) == (parsed_dev.port or 5432)
                and (parsed_test.database or "").lower() == (parsed_dev.database or "").lower()
            )
        ):
            raise ValueError(
                "TEST_DATABASE_URL cannot point to the development database. Tests require an isolated test database."
            )

        # Check 2: Database name must clearly indicate a test database
        db_name = (parsed_test.database or "").lower()
        if not ("test" in db_name or db_name.endswith("_test")):
            raise ValueError(
                f"TEST_DATABASE_URL database name '{db_name}' does not indicate a test database. It must contain 'test' or '_test'."
            )

        return test_url_clean

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
