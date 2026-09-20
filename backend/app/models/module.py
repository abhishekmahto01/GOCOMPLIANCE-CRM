"""Module Master model definition."""
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
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user_module_permission import UserModulePermission


class Module(Base):
    """Module Master table representing application modules, sub-modules and navigation routes."""

    __tablename__ = "module_master"
    __table_args__ = (
        CheckConstraint(
            "module_code ~ '^[A-Z_]+$'",
            name="chk_module_code_format",
        ),
        CheckConstraint(
            "route IS NULL OR route ~ '^/'",
            name="chk_module_route_format",
        ),
        CheckConstraint(
            "display_order >= 0",
            name="chk_module_display_order_non_negative",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_module_status_valid",
        ),
        CheckConstraint(
            "parent_module_id IS NULL OR parent_module_id <> module_id",
            name="chk_module_self_parent",
        ),
        {"comment": "Master registry for application modules, sub-modules and navigation hierarchy"},
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the module (UUIDv4)",
    )

    module_code: Mapped[str] = mapped_column(
        String(60),
        unique=True,
        nullable=False,
        index=True,
        comment="Uppercase unique system identifier (e.g., ADMIN, ADMIN_COMPANIES)",
    )

    module_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name of the module (e.g., Admin, Companies, Sales)",
    )

    parent_module_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "module_master.module_id",
            ondelete="RESTRICT",
            name="fk_module_parent_module_id",
        ),
        nullable=True,
        index=True,
        comment="Nullable self-referencing foreign key to parent module (ON DELETE RESTRICT)",
    )

    route: Mapped[Optional[str]] = mapped_column(
        String(200),
        unique=True,
        nullable=True,
        index=True,
        comment="Frontend route path starting with '/' (unique if provided)",
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional description of module features",
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        index=True,
        comment="Display sorting order (>= 0; lower value = higher priority)",
    )

    is_navigation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
        comment="Whether module should appear in UI navigation (does not grant permission)",
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
        comment="Timestamp when module record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when module record was last updated (UTC)",
    )

    # Self-referencing ORM Relationships
    parent: Mapped[Optional["Module"]] = relationship(
        "Module",
        remote_side=[module_id],
        back_populates="children",
    )

    children: Mapped[List["Module"]] = relationship(
        "Module",
        back_populates="parent",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    user_permissions: Mapped[List["UserModulePermission"]] = relationship(
        "UserModulePermission",
        back_populates="module",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Module(code='{self.module_code}', "
            f"name='{self.module_name}', "
            f"route='{self.route}', "
            f"order={self.display_order}, "
            f"status='{self.status}')>"
        )
