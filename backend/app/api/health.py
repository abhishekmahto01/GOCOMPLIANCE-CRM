from typing import Optional

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.services.database_health import check_database_health

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str


class DatabaseHealthResponse(BaseModel):
    status: str
    service: str
    database: Optional[str] = None
    detail: Optional[str] = None


@router.get("/health", response_model=HealthResponse, summary="API Health Check")
async def get_health() -> HealthResponse:
    """Return health status of the main CRM API service."""
    return HealthResponse(
        status="healthy",
        service="gocompliance-api",
    )


@router.get(
    "/health/database",
    response_model=DatabaseHealthResponse,
    responses={
        200: {"description": "Database connection healthy"},
        503: {"description": "Database connection unavailable"},
    },
    summary="Database Health Check",
)
def get_database_health(response: Response) -> DatabaseHealthResponse:
    """Check connectivity to PostgreSQL database."""
    is_healthy, payload = check_database_health()
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return DatabaseHealthResponse(**payload)
