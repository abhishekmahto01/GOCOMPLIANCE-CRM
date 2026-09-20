from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get("/health", response_model=HealthResponse, summary="API Health Check")
async def get_health() -> HealthResponse:
    """Return health status of the main CRM API service."""
    return HealthResponse(
        status="healthy",
        service="gocompliance-api",
    )
