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
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Database URL placeholder (Stage 2 implementation)
    DATABASE_URL: str | None = None

    @field_validator("CORS_ORIGINS", mode="before")
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
