"""User Master model definition."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.client import ClientMaster
    from app.models.company import Company
    from app.models.department import Department
    from app.models.designation import Designation
    from app.models.operation_application import OperationApplication
    from app.models.permission_audit import PermissionAuditLog
    from app.models.refresh_token import RefreshToken
    from app.models.sales_order import SalesOrder
    from app.models.user_module_permission import UserModulePermission


class User(Base):
    """User Master table representing employees / user accounts in Gocompliances CRM."""

    __tablename__ = "user_master"
    __table_args__ = (
        CheckConstraint(
            "manager_user_id IS NULL OR manager_user_id <> user_id",
            name="chk_user_self_manager",
        ),
        CheckConstraint(
            "employment_type IN ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERN', 'CONSULTANT')",
            name="chk_user_employment_type_valid",
        ),
        CheckConstraint(
            "account_status IN ('PENDING', 'ACTIVE', 'INACTIVE', 'SUSPENDED')",
            name="chk_user_account_status_valid",
        ),
        CheckConstraint(
            "failed_login_attempts >= 0",
            name="chk_user_failed_login_attempts_non_negative",
        ),
        CheckConstraint(
            "token_version > 0",
            name="chk_user_token_version_positive",
        ),
        Index(
            "ix_user_master_official_email_lower",
            func.lower(text("official_email")),
            unique=True,
        ),
        {"comment": "Master registry for employees/users in Gocompliances CRM"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the user / employee (UUIDv4)",
    )

    employee_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Globally unique uppercase employee code (e.g. CG0001, EP0001, BM0001)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_user_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id (ON DELETE RESTRICT)",
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "department_master.department_id",
            ondelete="RESTRICT",
            name="fk_user_department_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing department_master.department_id (ON DELETE RESTRICT)",
    )

    designation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "designation_master.designation_id",
            ondelete="RESTRICT",
            name="fk_user_designation_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing designation_master.designation_id (ON DELETE RESTRICT)",
    )

    manager_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_user_manager_user_id",
        ),
        nullable=True,
        index=True,
        comment="Nullable self-referencing foreign key to reporting manager (ON DELETE SET NULL)",
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Employee first name",
    )

    middle_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Employee middle name (optional)",
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Employee last name",
    )

    official_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Official corporate email address (case-insensitively unique)",
    )

    personal_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Personal email address (optional)",
    )

    mobile_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Primary contact mobile number (e.g. +91XXXXXXXXXX)",
    )

    date_of_joining: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Official date of joining",
    )

    employment_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Employment type: FULL_TIME, PART_TIME, CONTRACT, INTERN, CONSULTANT",
    )

    account_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'PENDING'"),
        index=True,
        comment="Account/employment status: PENDING, ACTIVE, INACTIVE, SUSPENDED",
    )

    is_hod: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Whether user is designated as Head of Department (HOD)",
    )

    is_reporting_manager: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        default=False,
        comment="Whether user is designated as a Reporting Manager",
    )

    primary_location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Primary operating location / branch of the employee",
    )

    # Security & Authentication fields (Stage 7B)
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Argon2id password hash (nullable until user activates account)",
    )

    must_change_password: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
        comment="Flag indicating if password change is required on next login",
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Counter for consecutive failed login attempts",
    )

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp until which account is locked due to failed login attempts",
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of most recent successful login (UTC)",
    )

    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when password was last changed (UTC)",
    )

    credentials_initialized_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when credentials were first provisioned (UTC)",
    )

    token_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
        comment="Session token version for global revocation",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when user record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when user record was last updated (UTC)",
    )

    # ORM Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="users",
    )

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="users",
    )

    designation: Mapped["Designation"] = relationship(
        "Designation",
        back_populates="users",
    )

    manager: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side=[user_id],
        back_populates="direct_reports",
    )

    direct_reports: Mapped[List["User"]] = relationship(
        "User",
        back_populates="manager",
    )

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    module_permissions: Mapped[List["UserModulePermission"]] = relationship(
        "UserModulePermission",
        foreign_keys="[UserModulePermission.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    permissions_granted: Mapped[List["UserModulePermission"]] = relationship(
        "UserModulePermission",
        foreign_keys="[UserModulePermission.granted_by_user_id]",
        back_populates="granted_by",
    )

    audit_actions_performed: Mapped[List["PermissionAuditLog"]] = relationship(
        "PermissionAuditLog",
        foreign_keys="[PermissionAuditLog.actor_user_id]",
        back_populates="actor",
    )

    audit_logs_received: Mapped[List["PermissionAuditLog"]] = relationship(
        "PermissionAuditLog",
        foreign_keys="[PermissionAuditLog.target_user_id]",
        back_populates="target_user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    clients_created: Mapped[List["ClientMaster"]] = relationship(
        "ClientMaster",
        foreign_keys="[ClientMaster.created_by_user_id]",
        back_populates="created_by",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    sales_orders: Mapped[List["SalesOrder"]] = relationship(
        "SalesOrder",
        foreign_keys="[SalesOrder.salesperson_user_id]",
        back_populates="salesperson",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    assigned_applications: Mapped[List["OperationApplication"]] = relationship(
        "OperationApplication",
        foreign_keys="[OperationApplication.assigned_to_user_id]",
        back_populates="assigned_to",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    applications_assigned_by: Mapped[List["OperationApplication"]] = relationship(
        "OperationApplication",
        foreign_keys="[OperationApplication.assigned_by_user_id]",
        back_populates="assigned_by",
    )

    def __repr__(self) -> str:
        return (
            f"<User(code='{self.employee_code}', "
            f"name='{self.first_name} {self.last_name}', "
            f"email='{self.official_email}', "
            f"status='{self.account_status}')>"
        )
