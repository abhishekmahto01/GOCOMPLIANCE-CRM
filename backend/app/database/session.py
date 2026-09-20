"""Database engine, session factory, and session dependency."""
import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure connect_args for driver timeout
connect_args = {}
if settings.DATABASE_URL.startswith("postgresql"):
    connect_args["connect_timeout"] = settings.DB_CONNECT_TIMEOUT

# Create SQLAlchemy 2 engine with connection health pre-ping
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    connect_args=connect_args,
)

# Session factory for synchronous SQLAlchemy sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a SQLAlchemy session.

    Guarantees session cleanup via try/finally block.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
