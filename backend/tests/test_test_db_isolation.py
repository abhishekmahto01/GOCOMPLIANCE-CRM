"""Unit tests for Test Database Isolation and Configuration Safety Guards."""
import pytest
from app.core.config import Settings


def test_missing_test_database_url_rejected() -> None:
    """Verify that empty or None TEST_DATABASE_URL is rejected with a clear error."""
    dev_url = "postgresql+psycopg://abhishekmahto@localhost:5432/is_gocompliance_db"

    with pytest.raises(ValueError) as exc_info:
        Settings.validate_test_database_isolation(test_url=None, dev_url=dev_url)
    assert "TEST_DATABASE_URL is not configured" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        Settings.validate_test_database_isolation(test_url="   ", dev_url=dev_url)
    assert "TEST_DATABASE_URL is not configured" in str(exc_info.value)


def test_development_database_url_rejected() -> None:
    """Verify that pointing TEST_DATABASE_URL to the development database is strictly rejected."""
    dev_url = "postgresql+psycopg://dbuser:secretpass123@localhost:5432/is_gocompliance_db"

    # Exact same URL
    with pytest.raises(ValueError) as exc_info:
        Settings.validate_test_database_isolation(test_url=dev_url, dev_url=dev_url)
    assert "cannot point to the development database" in str(exc_info.value)
    assert "secretpass123" not in str(exc_info.value)

    # Same host/port/database with different formatting or protocol prefix
    test_same_db = "postgresql://dbuser:differentpass@localhost:5432/is_gocompliance_db"
    with pytest.raises(ValueError) as exc_info:
        Settings.validate_test_database_isolation(test_url=test_same_db, dev_url=dev_url)
    assert "cannot point to the development database" in str(exc_info.value)
    assert "differentpass" not in str(exc_info.value)


def test_non_test_database_name_rejected() -> None:
    """Verify that database names not containing 'test' or '_test' are rejected."""
    dev_url = "postgresql+psycopg://abhishekmahto@localhost:5432/is_gocompliance_db"
    prod_like_test_url = "postgresql+psycopg://abhishekmahto@localhost:5432/production_replica"

    with pytest.raises(ValueError) as exc_info:
        Settings.validate_test_database_isolation(test_url=prod_like_test_url, dev_url=dev_url)
    assert "does not indicate a test database" in str(exc_info.value)
    assert "production_replica" in str(exc_info.value)


def test_valid_test_database_url_accepted() -> None:
    """Verify that dedicated test database URLs are accepted and normalized."""
    dev_url = "postgresql+psycopg://abhishekmahto@localhost:5432/is_gocompliance_db"
    valid_test_url = "postgresql+psycopg://abhishekmahto@localhost:5432/is_gocompliance_test_db"

    result = Settings.validate_test_database_isolation(test_url=valid_test_url, dev_url=dev_url)
    assert result == valid_test_url

    # postgresql:// shorthand normalized to postgresql+psycopg://
    shorthand_url = "postgresql://abhishekmahto@localhost:5432/crm_app_test"
    result_normalized = Settings.validate_test_database_isolation(test_url=shorthand_url, dev_url=dev_url)
    assert result_normalized == "postgresql+psycopg://abhishekmahto@localhost:5432/crm_app_test"


def test_credentials_not_exposed_in_masked_urls() -> None:
    """Verify that masked_test_database_url hides plain passwords."""
    settings_with_pw = Settings(
        DATABASE_URL="postgresql+psycopg://dbuser:supersecretpass@localhost:5432/is_gocompliance_db",
        TEST_DATABASE_URL="postgresql+psycopg://testuser:supersecrettestpass@localhost:5432/is_gocompliance_test_db",
    )
    assert "supersecrettestpass" not in settings_with_pw.masked_test_database_url
    assert "***" in settings_with_pw.masked_test_database_url
    assert "testuser" in settings_with_pw.masked_test_database_url
    assert "is_gocompliance_test_db" in settings_with_pw.masked_test_database_url
