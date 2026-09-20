from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.base import Base
from app.database.session import get_db
from app.services.database_health import check_database_health


def test_get_db_session_lifecycle() -> None:
    """Verify that get_db yields a session and guarantees close() is called."""
    mock_session = MagicMock(spec=Session)

    with patch("app.database.session.SessionLocal", return_value=mock_session):
        db_generator = get_db()
        session = next(db_generator)

        assert session is mock_session
        assert mock_session.close.call_count == 0

        # Terminating generator should trigger finally: db.close()
        with pytest.raises(StopIteration):
            next(db_generator)

        assert mock_session.close.call_count == 1


def test_config_password_masking() -> None:
    """Verify that sensitive database credentials are masked by Settings."""
    # With password
    settings_with_pw = Settings(
        DATABASE_URL="postgresql+psycopg://dbuser:supersecretpass@localhost:5432/is_gocompliance_db"
    )
    assert "supersecretpass" not in settings_with_pw.masked_database_url
    assert "***" in settings_with_pw.masked_database_url
    assert "dbuser" in settings_with_pw.masked_database_url
    assert "is_gocompliance_db" in settings_with_pw.masked_database_url

    # Without password
    settings_no_pw = Settings(
        DATABASE_URL="postgresql+psycopg://abhishekmahto@localhost:5432/is_gocompliance_db"
    )
    assert "abhishekmahto" in settings_no_pw.masked_database_url
    assert "is_gocompliance_db" in settings_no_pw.masked_database_url


def test_config_missing_database_url() -> None:
    """Verify that empty or missing DATABASE_URL raises a clear validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(DATABASE_URL="")
    assert "DATABASE_URL is not configured" in str(exc_info.value)


def test_no_tables_created_in_stage_2() -> None:
    """Verify that Base.metadata contains no tables in Stage 2."""
    assert len(Base.metadata.tables) == 0


def test_database_health_service_success() -> None:
    """Verify check_database_health returns healthy when query succeeds."""
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (1, "is_gocompliance_db")
    mock_conn.execute.return_value = mock_result
    mock_conn.__enter__.return_value = mock_conn

    with patch("app.services.database_health.engine.connect", return_value=mock_conn):
        is_healthy, payload = check_database_health()
        assert is_healthy is True
        assert payload == {
            "status": "healthy",
            "service": "postgresql",
            "database": "is_gocompliance_db",
        }


def test_database_health_service_failure() -> None:
    """Verify check_database_health handles connection errors gracefully."""
    with patch(
        "app.services.database_health.engine.connect",
        side_effect=Exception("Connection refused"),
    ):
        is_healthy, payload = check_database_health()
        assert is_healthy is False
        assert payload == {
            "status": "unhealthy",
            "service": "postgresql",
            "detail": "Database connection unavailable",
        }
        # Verify raw exception is not exposed in payload
        assert "Connection refused" not in str(payload)
