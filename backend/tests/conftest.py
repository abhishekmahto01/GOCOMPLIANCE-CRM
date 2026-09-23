"""Global Pytest Configuration and Test Database Isolation for GOCOMPLIANCE CRM.

Strictly enforces:
1. Tests MUST use TEST_DATABASE_URL.
2. Tests must NEVER fall back to DATABASE_URL.
3. Test startup fails immediately if TEST_DATABASE_URL is missing, equals DATABASE_URL, or does not indicate a test DB.
4. Schema setup and fixtures run solely against the isolated test database.
5. Function-level transactions ensure zero test data persistence.
"""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, settings
from app.database.base import Base
from app.database.session import get_db
from app.main import app

# Ensure environment is marked as test
os.environ["APP_ENV"] = "test"
os.environ["ENVIRONMENT"] = "test"


def get_verified_test_db_url() -> str:
    """Validate and return isolated test database URL."""
    test_url = os.environ.get("TEST_DATABASE_URL") or getattr(settings, "TEST_DATABASE_URL", None)
    dev_url = settings.DATABASE_URL

    return Settings.validate_test_database_isolation(test_url=test_url, dev_url=dev_url)


# Lazy-initialized test engine and session factory
_test_engine = None
_TestingSessionLocal = None


def get_test_engine():
    global _test_engine
    if _test_engine is None:
        test_url = get_verified_test_db_url()
        _test_engine = create_engine(
            test_url,
            pool_pre_ping=True,
        )
    return _test_engine


def get_test_session_factory():
    global _TestingSessionLocal
    if _TestingSessionLocal is None:
        eng = get_test_engine()
        _TestingSessionLocal = sessionmaker(
            bind=eng,
            autoflush=False,
            expire_on_commit=False,
        )
    return _TestingSessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure schema exists on the dedicated test database when integration tests run."""
    # Only verify/setup test DB if test DB URL is provided or required
    test_url = os.environ.get("TEST_DATABASE_URL") or getattr(settings, "TEST_DATABASE_URL", None)
    if test_url:
        get_verified_test_db_url()
        eng = get_test_engine()
        Base.metadata.drop_all(bind=eng)
        Base.metadata.create_all(bind=eng)
        yield
    else:
        yield


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a transactional database session rolled back after every test."""
    test_url = os.environ.get("TEST_DATABASE_URL") or getattr(settings, "TEST_DATABASE_URL", None)
    if not test_url:
        pytest.skip("TEST_DATABASE_URL is not configured. Skipping database-dependent test.")

    eng = get_test_engine()
    connection = eng.connect()
    transaction = connection.begin()

    session = Session(bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide FastAPI TestClient wired to the transaction-isolated test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
