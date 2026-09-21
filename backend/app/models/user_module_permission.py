"""User Module Permission model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.module import Module
    from app.models.user import User


class UserModulePermission(Base):
    """Per-User Module Permission table defining granular action rights and data scopes."""

    __tablename__ = "user_module_permission"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "module_id",
            name="uq_user_module_permission_user_module",
        ),
        CheckConstraint(
            "data_scope IN ('SELF', 'TEAM', 'DEPARTMENT', 'COMPANY', 'ALL')",
            name="chk_permission_data_scope_valid",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_permission_status_valid",
        ),
        CheckConstraint(
            "can_view = true OR (can_create = false AND can_edit = false AND can_delete = false AND can_approve = false AND can_assign = false AND can_reassign = false AND can_export = false)",
            name="chk_permission_action_requires_view",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at > granted_at",
            name="chk_permission_expires_after_granted",
        ),
        {"comment": "Per-user granular permissions and data scope assignments for CRM modules"},
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the permission grant (UUIDv4)",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="CASCADE",
            name="fk_permission_user_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing target user (ON DELETE CASCADE)",
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "module_master.module_id",
            ondelete="RESTRICT",
            name="fk_permission_module_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing target module (ON DELETE RESTRICT)",
    )

    can_view: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to view module page and query records within data scope",
    )

    can_create: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to create new records in module (requires can_view=true)",
    )

    can_edit: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to edit records in module (requires can_view=true)",
    )

    can_delete: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to delete/deactivate records in module (requires can_view=true)",
    )

    can_approve: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to execute approval workflows in module (requires can_view=true)",
    )

    can_assign: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to assign orders/tasks in module (requires can_view=true)",
    )

    can_reassign: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to reassign orders/tasks in module (requires can_view=true)",
    )

    can_export: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Permission to export reports/records in module (requires can_view=true)",
    )

    data_scope: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'SELF'"),
        default="SELF",
        comment="Data visibility scope: SELF, TEAM, DEPARTMENT, COMPANY, ALL",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
        default="ACTIVE",
        index=True,
        comment="Permission status: ACTIVE or INACTIVE",
    )

    granted_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_permission_granted_by_user_id",
        ),
        nullable=True,
        index=True,
        comment="Nullable foreign key to grantor user (ON DELETE SET NULL)",
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when permission was granted (UTC)",
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Optional expiration timestamp for temporary access (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when permission record was last updated (UTC)",
    )

    # ORM Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="module_permissions",
    )

    module: Mapped["Module"] = relationship(
        "Module",
        foreign_keys=[module_id],
        back_populates="user_permissions",
    )

    granted_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[granted_by_user_id],
        back_populates="permissions_granted",
    )

    def __repr__(self) -> str:
        return (
            f"<UserModulePermission(id='{self.permission_id}', "
            f"user_id='{self.user_id}', "
            f"module_id='{self.module_id}', "
            f"scope='{self.data_scope}', "
            f"view={self.can_view}, "
            f"create={self.can_create}, "
            f"edit={self.can_edit}, "
            f"delete={self.can_delete}, "
            f"approve={self.can_approve}, "
            f"assign={self.can_assign}, "
            f"reassign={self.can_reassign}, "
            f"export={self.can_export}, "
            f"status='{self.status}')>"
        )
