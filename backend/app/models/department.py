"""Department Master model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.company import Company


class Department(Base):
    """Department Master table representing company-specific organizational departments."""

    __tablename__ = "department_master"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "department_code",
            name="uq_department_company_code",
        ),
        UniqueConstraint(
            "company_id",
            "department_name",
            name="uq_department_company_name",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_department_status_valid",
        ),
        CheckConstraint(
            "department_code ~ '^[A-Z_]+$'",
            name="chk_department_code_format",
        ),
        {"comment": "Master registry for company-specific departments in Gocompliances CRM"},
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the department (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_department_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id (ON DELETE RESTRICT)",
    )

    department_code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Uppercase department code unique per company (e.g., ADMINISTRATION, SALES)",
    )

    department_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name of the department (e.g., Administration, Sales, R&D)",
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

    # ORM Relationship to Company
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="departments",
    )

    def __repr__(self) -> str:
        return (
            f"<Department(code='{self.department_code}', "
            f"name='{self.department_name}', "
            f"company_id='{self.company_id}', "
            f"status='{self.status}')>"
        )
