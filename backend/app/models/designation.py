"""Designation Master model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
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
    from app.models.user import User


class Designation(Base):
    """Designation Master table representing company-specific employee designations/job titles."""

    __tablename__ = "designation_master"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "designation_code",
            name="uq_designation_company_code",
        ),
        UniqueConstraint(
            "company_id",
            "designation_name",
            name="uq_designation_company_name",
        ),
        CheckConstraint(
            "level_rank > 0",
            name="chk_designation_level_rank_positive",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_designation_status_valid",
        ),
        CheckConstraint(
            "designation_code ~ '^[A-Z_]+$'",
            name="chk_designation_code_format",
        ),
        {"comment": "Master registry for company-specific employee designations in Gocompliances CRM"},
    )

    designation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the designation (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_designation_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id (ON DELETE RESTRICT)",
    )

    designation_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Uppercase designation code unique per company (e.g., EXECUTIVE, MANAGER)",
    )

    designation_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display job title of the designation (e.g., Executive, Manager, Director)",
    )

    level_rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Seniority level ranking counter (>0; higher value = higher seniority)",
    )

    is_managerial: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Classification flag indicating managerial position (informational only; does not grant permissions)",
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional description of the designation responsibilities",
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
        comment="Timestamp when designation record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when designation record was last updated (UTC)",
    )

    # ORM Relationship to Company
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="designations",
    )

    # ORM Relationship to User (Restrictive deletion; no cascade delete)
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="designation",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Designation(code='{self.designation_code}', "
            f"name='{self.designation_name}', "
            f"rank={self.level_rank}, "
            f"managerial={self.is_managerial}, "
            f"status='{self.status}')>"
        )
