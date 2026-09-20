"""SQLAlchemy declarative base."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative Base class for all SQLAlchemy ORM models.

    Stage 2 Note: Models and schema migrations will be created in Stage 3.
    Do not call Base.metadata.create_all() in Stage 2.
    """
    pass
