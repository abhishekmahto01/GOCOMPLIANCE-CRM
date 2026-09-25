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


class OperationRemarkCreate(BaseModel):
    """Schema for recording a new operations remark on a task."""

    remark_text: str = Field(..., min_length=1, max_length=2000, description="Remark explanation or status update text")

    @field_validator("remark_text", mode="before")
    @classmethod
    def validate_remark_text(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Remark text cannot be empty.")
        return v.strip()


class OperationRemarkRead(BaseModel):
    """Read schema for operations remark history."""

    remark_id: uuid.UUID
    application_id: uuid.UUID
    author_user_id: uuid.UUID
    author_name: str
    author_employee_code: Optional[str] = None
    author_department: Optional[str] = None
    author_designation: Optional[str] = None
    remark_text: str
    created_at: datetime
    formatted_created_at: Optional[str] = None

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
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    service_id: uuid.UUID
    service_name: Optional[str] = None
    service_code: Optional[str] = None
    salesperson_name: Optional[str] = None
    salesperson_code: Optional[str] = None
    assigned_to_user_id: Optional[uuid.UUID] = None
    assigned_to_name: Optional[str] = None
    assigned_to_code: Optional[str] = None
    assigned_by_user_id: Optional[uuid.UUID] = None
    assigned_by_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    formatted_assigned_at: Optional[str] = None
    priority: str
    application_status: str
    target_due_date: Optional[date] = None
    formatted_due_date: Optional[str] = None
    completion_date: Optional[date] = None
    assignment_notes: Optional[str] = None
    documents_completed: int = 0
    documents_total: int = 0
    is_overdue: bool = False
    is_due_soon: bool = False
    order_date: Optional[date] = None
    formatted_order_date: Optional[str] = None
    latest_remark: Optional[OperationRemarkRead] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperationApplicationDetailRead(OperationApplicationRead):
    """Comprehensive read schema for application detail page."""

    documents: List[ApplicationDocRead] = Field(default_factory=list)
    assignment_history: List[AssignmentHistoryRead] = Field(default_factory=list)
    activity_logs: List[ActivityLogRead] = Field(default_factory=list)
    remarks: List[OperationRemarkRead] = Field(default_factory=list)

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
    notes: Optional[str] = None


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


class OperationsKpiSummary(BaseModel):
    """Top KPI metrics for Operations Dashboard."""

    total_applications: int = 0
    assigned_count: int = 0
    in_progress_count: int = 0
    pending_documents_count: int = 0
    ready_submitted_count: int = 0
    authority_query_count: int = 0
    approved_count: int = 0
    overdue_count: int = 0
    unassigned_count: int = 0
    sla_adherence_percent: float = 100.0


class OperationsStatusBreakdownItem(BaseModel):
    """Status distribution breakdown item for charts."""

    status: str
    label: str
    count: int
    percentage: float
    color: str


class ExecutiveWorkloadItem(BaseModel):
    """Workload and throughput metrics for an Operations team member."""

    user_id: uuid.UUID
    employee_code: str
    full_name: str
    designation_name: Optional[str] = None
    active_tasks: int = 0
    in_progress_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    sla_rating: float = 100.0


class OperationsTaskSummary(BaseModel):
    """Summary counts for task list header strips."""

    total_tasks: int = 0
    assigned: int = 0
    in_progress: int = 0
    pending_docs: int = 0
    under_review: int = 0
    completed: int = 0
    overdue: int = 0


class OperationsTaskListResponse(BaseModel):
    """Paginated list of operations tasks."""

    items: List[OperationApplicationRead]
    total_count: int
    page: int
    limit: int
    total_pages: int
    summary: OperationsTaskSummary


class OperationsDashboardResponse(BaseModel):
    """Full live response for Operations Dashboard analytics."""

    kpis: OperationsKpiSummary
    status_breakdown: List[OperationsStatusBreakdownItem]
    workload_by_executive: List[ExecutiveWorkloadItem]
    recent_applications: List[OperationApplicationRead]
    priority_queue: List[OperationApplicationRead]
    scope: str
    company_id: uuid.UUID
    company_name: str
