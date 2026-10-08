"""Operations Coordinator Configuration model mapping company to default Operations coordinator."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class OperationsCoordinatorConfig(Base):
    """Configuration mapping a business company to its default Operations coordinator."""

    __tablename__ = "operations_coordinator_config"
    __table_args__ = (
        UniqueConstraint("company_id", name="uq_operations_coordinator_company_id"),
        {"comment": "Configuration mapping Sales entry company to default Operations coordinator"},
    )

    config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the configuration record",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("company_master.company_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the company (company_master)",
    )

    coordinator_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_master.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the default Operations coordinator user (user_master)",
    )

    updated_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_master.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="Admin user who last updated this configuration",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when config was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when config was last updated (UTC)",
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", lazy="joined")
    coordinator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[coordinator_user_id],
        lazy="joined",
    )
    updated_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_user_id],
        lazy="joined",
    )
