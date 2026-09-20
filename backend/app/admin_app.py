from fastapi import FastAPI
from pydantic import BaseModel

from app.core.config import settings

app = FastAPI(
    title=settings.ADMIN_PROJECT_NAME,
    version=settings.VERSION,
    description="Database Admin panel placeholder for Gocompliances CRM",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


class AdminHealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=AdminHealthResponse, summary="Admin Health Check")
async def health_check() -> AdminHealthResponse:
    """Return health status of the Admin Panel service."""
    return AdminHealthResponse(
        status="healthy",
        service="gocompliance-admin",
    )
