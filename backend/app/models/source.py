"""Source Master model definition for managing lead acquisition channels."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SourceMaster(Base):
    """Source Master table representing lead acquisition channels across Gocompliances CRM."""

    __tablename__ = "source_master"
    __table_args__ = (
        UniqueConstraint("source_code", name="uq_source_code"),
        UniqueConstraint("source_name", name="uq_source_name"),
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="chk_source_status_valid"),
        CheckConstraint("source_code ~ '^[A-Z0-9_]+$'", name="chk_source_code_format"),
        {"comment": "Master registry for lead acquisition sources and marketing channels"},
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    source_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Uppercase unique identifier for source, e.g. WEBSITE, JUSTDIAL, GOOGLE_ADS",
    )

    source_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name for source, e.g. Website, Justdial, IndiaMART, Google Ads",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional description or details about the acquisition source",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
        comment="ACTIVE or INACTIVE",
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Flag indicating system-seeded default source",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

