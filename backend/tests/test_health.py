import pytest
from fastapi.testclient import TestClient

from app.admin_app import app as admin_app
from app.main import app as main_app


@pytest.fixture
def main_client() -> TestClient:
    """Fixture providing a TestClient for the main CRM API."""
    return TestClient(main_app)


@pytest.fixture
def admin_client() -> TestClient:
    """Fixture providing a TestClient for the Admin application."""
    return TestClient(admin_app)


def test_main_api_health(main_client: TestClient) -> None:
    """Test that GET /api/health on main API returns 200 and expected payload."""
    response = main_client.get("/api/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "status": "healthy",
        "service": "gocompliance-api",
    }


def test_admin_app_health(admin_client: TestClient) -> None:
    """Test that GET /health on Admin app returns 200 and expected payload."""
    response = admin_client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "status": "healthy",
        "service": "gocompliance-admin",
    }
