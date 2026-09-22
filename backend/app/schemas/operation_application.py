"""Pydantic schemas for Operations Applications, Documents, Assignments, and Status Changes."""
import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApplicationDocRead(BaseModel):
    """Read schema for application document requirement."""

    app_doc_id: uuid.UUID
    application_id: uuid.UUID
    document_code: str
    document_name: str
    is_mandatory: bool
    status: str
    rejection_reason: Optional[str] = None
    verified_by_user_id: Optional[uuid.UUID] = None
    verified_by_name: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationDocUpdate(BaseModel):
    """Schema for updating document verification state."""

    status: str = Field(..., description="PENDING, RECEIVED, VERIFIED, REJECTED, NOT_APPLICABLE")
    rejection_reason: Optional[str] = Field(None, max_length=500)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_doc_status(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ("PENDING", "RECEIVED", "VERIFIED", "REJECTED", "NOT_APPLICABLE"):
                raise ValueError(f"Invalid document status '{v}'")
        return v


class AssignmentHistoryRead(BaseModel):
    """Read schema for assignment history entries."""

    history_id: uuid.UUID
    application_id: uuid.UUID
    assigned_by_user_id: uuid.UUID
    assigned_by_name: Optional[str] = None
    previous_assignee_user_id: Optional[uuid.UUID] = None
    previous_assignee_name: Optional[str] = None
    new_assignee_user_id: Optional[uuid.UUID] = None
    new_assignee_name: Optional[str] = None
    reason: Optional[str] = None
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityLogRead(BaseModel):
    """Read schema for application timeline entries."""

    activity_id: uuid.UUID
    application_id: uuid.UUID
    actor_user_id: uuid.UUID
    actor_name: Optional[str] = None
    action_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperationApplicationRead(BaseModel):
    """Read schema for Operation Application."""

    application_id: uuid.UUID
    application_number: str
    sales_order_id: uuid.UUID
    sales_order_number: Optional[str] = None
    company_id: uuid.UUID
    client_id: uuid.UUID
    client_name: Optional[str] = None
    service_id: uuid.UUID
    service_name: Optional[str] = None
    assigned_to_user_id: Optional[uuid.UUID] = None
    assigned_to_name: Optional[str] = None
    assigned_by_user_id: Optional[uuid.UUID] = None
    assigned_at: Optional[datetime] = None
    priority: str
    application_status: str
    target_due_date: Optional[date] = None
    completion_date: Optional[date] = None
    assignment_notes: Optional[str] = None
    documents_completed: int = 0
    documents_total: int = 0
    is_overdue: bool = False
    is_due_soon: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperationApplicationDetailRead(OperationApplicationRead):
    """Comprehensive read schema for application detail page."""

    documents: List[ApplicationDocRead] = Field(default_factory=list)
    assignment_history: List[AssignmentHistoryRead] = Field(default_factory=list)
    activity_logs: List[ActivityLogRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TaskAssignRequest(BaseModel):
    """Schema for assigning an unassigned application to an operations employee."""

    assignee_user_id: uuid.UUID
    priority: Optional[str] = Field(default="MEDIUM")
    target_due_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ("LOW", "MEDIUM", "HIGH", "URGENT"):
                raise ValueError(f"Invalid priority '{v}'")
            return v
        return "MEDIUM"


class TaskReassignRequest(BaseModel):
    """Schema for reassigning an application to a new operations employee."""

    new_assignee_user_id: uuid.UUID
    reason: str = Field(..., min_length=2, max_length=500, description="Mandatory reason for reassignment")
    priority: Optional[str] = None
    target_due_date: Optional[date] = None


class ApplicationStatusUpdateRequest(BaseModel):
    """Schema for transitioning application lifecycle status."""

    new_status: str = Field(..., description="Target status")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment or filing reference")

    @field_validator("new_status", mode="before")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            valid_statuses = (
                "UNASSIGNED",
                "ASSIGNED",
                "IN_PROGRESS",
                "PENDING_DOCUMENTS",
                "READY_FOR_SUBMISSION",
                "SUBMITTED",
                "AUTHORITY_QUERY",
                "APPROVED",
                "CANCELLED",
            )
            if v not in valid_statuses:
                raise ValueError(f"Invalid application status '{v}'")
        return v
