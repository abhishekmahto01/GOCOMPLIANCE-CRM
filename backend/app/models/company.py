"""Company Master model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.designation import Designation
    from app.models.user import User


class Company(Base):
    """Company Master table representing business entities operating in Gocompliances CRM."""

    __tablename__ = "company_master"
    __table_args__ = (
        CheckConstraint(
            "next_employee_number > 0",
            name="chk_company_next_employee_number_positive",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_company_status_valid",
        ),
        CheckConstraint(
            "employee_code_prefix ~ '^[A-Z]{2,5}$'",
            name="chk_company_employee_code_prefix_format",
        ),
        {"comment": "Master registry for companies operating within Gocompliances CRM"},
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the company (UUIDv4)",
    )

    company_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique uppercase business identifier code (e.g., GOCOMPLIANCES)",
    )

    company_name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
        comment="Primary trade/display name of the company",
    )

    legal_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Registered legal/corporate entity name (optional)",
    )

    employee_code_prefix: Mapped[str] = mapped_column(
        String(5),
        unique=True,
        nullable=False,
        comment="2-5 character uppercase prefix for employee IDs (e.g. CG, EP, BM)",
    )

    next_employee_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
        comment="Sequential counter for next employee code assignment (>0)",
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
        comment="Timestamp when company record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when company record was last updated (UTC)",
    )

    # ORM Relationship to Department (Restrictive deletion; no cascade delete)
    departments: Mapped[List["Department"]] = relationship(
        "Department",
        back_populates="company",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    # ORM Relationship to Designation (Restrictive deletion; no cascade delete)
    designations: Mapped[List["Designation"]] = relationship(
        "Designation",
        back_populates="company",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    # ORM Relationship to User (Restrictive deletion; no cascade delete)
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="company",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Company(code='{self.company_code}', "
            f"name='{self.company_name}', "
            f"prefix='{self.employee_code_prefix}', "
            f"status='{self.status}')>"
        )
