"""Department Master model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Department(Base):
    """Department Master table representing global organizational departments across all companies."""

    __tablename__ = "department_master"
    __table_args__ = (
        UniqueConstraint(
            "department_code",
            name="uq_department_code",
        ),
        UniqueConstraint(
            "department_name",
            name="uq_department_name",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_department_status_valid",
        ),
        CheckConstraint(
            "department_code ~ '^[A-Z_]+$'",
            name="chk_department_code_format",
        ),
        {"comment": "Global master registry for departments across all companies in Gocompliances CRM"},
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the department (UUIDv4)",
    )

    department_code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Uppercase department code unique globally (e.g., ADMINISTRATION, SALES, OPERATIONS, ACCOUNTS)",
    )

    department_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name of the department (e.g., Administration, Sales, Operations, Accounts, R&D)",
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional description of the department functions",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
        index=True,
        comment="Operational status: ACTIVE or INACTIVE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when department record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when department record was last updated (UTC)",
    )

    # ORM Relationship to User (Restrictive deletion; no cascade delete)
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="department",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Department(code='{self.department_code}', "
            f"name='{self.department_name}', "
            f"status='{self.status}')>"
        )
