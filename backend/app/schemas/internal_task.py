"""Pydantic schemas for the R&D / Internal Tasks feature."""
import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.internal_task import (
    INTERNAL_TASK_PRIORITIES,
    INTERNAL_TASK_STATUSES,
    INTERNAL_TASK_TYPES,
)


def _norm_choice(value: Optional[str], allowed: tuple, field: str) -> Optional[str]:
    if value is None:
        return None
    v = str(value).strip().upper()
    if v not in allowed:
        raise ValueError(f"Invalid {field} '{value}'. Allowed: {', '.join(allowed)}")
    return v


def _clean_text(value: Optional[str], field: str, required: bool = False) -> Optional[str]:
    if value is None:
        if required:
            raise ValueError(f"{field} is required")
        return None
    v = str(value).strip()
    if required and not v:
        raise ValueError(f"{field} cannot be blank")
    return v or None


class InternalTaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    task_type: str = Field("RESEARCH")
    priority: str = Field("MEDIUM")
    assigned_to_user_id: uuid.UUID
    due_date: Optional[date] = None

    @field_validator("title", mode="before")
    @classmethod
    def _title(cls, v):
        return _clean_text(v, "Title", required=True)

    @field_validator("description", mode="before")
    @classmethod
    def _desc(cls, v):
        return _clean_text(v, "Description")

    @field_validator("task_type", mode="before")
    @classmethod
    def _type(cls, v):
        return _norm_choice(v or "RESEARCH", INTERNAL_TASK_TYPES, "task type")

    @field_validator("priority", mode="before")
    @classmethod
    def _prio(cls, v):
        return _norm_choice(v or "MEDIUM", INTERNAL_TASK_PRIORITIES, "priority")


class InternalTaskUpdate(BaseModel):
    """Edit task details (creator or manager only)."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    task_type: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title", mode="before")
    @classmethod
    def _title(cls, v):
        return None if v is None else _clean_text(v, "Title", required=True)

    @field_validator("description", mode="before")
    @classmethod
    def _desc(cls, v):
        return _clean_text(v, "Description")

    @field_validator("task_type", mode="before")
    @classmethod
    def _type(cls, v):
        return _norm_choice(v, INTERNAL_TASK_TYPES, "task type")

    @field_validator("priority", mode="before")
    @classmethod
    def _prio(cls, v):
        return _norm_choice(v, INTERNAL_TASK_PRIORITIES, "priority")


class InternalTaskStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    comment: Optional[str] = Field(None, max_length=1000)

    @field_validator("status", mode="before")
    @classmethod
    def _status(cls, v):
        return _norm_choice(v, INTERNAL_TASK_STATUSES, "status")


class InternalTaskReassign(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assigned_to_user_id: uuid.UUID
    reason: Optional[str] = Field(None, max_length=1000)


class InternalTaskMessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_text: str = Field(..., min_length=1, max_length=5000)

    @field_validator("message_text", mode="before")
    @classmethod
    def _text(cls, v):
        return _clean_text(v, "Message", required=True)


class InternalTaskUserRef(BaseModel):
    user_id: uuid.UUID
    name: str
    employee_code: Optional[str] = None
    department_name: Optional[str] = None
    company_name: Optional[str] = None


class InternalTaskRead(BaseModel):
    task_id: uuid.UUID
    task_number: str
    company_id: uuid.UUID
    company_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    task_type: str
    priority: str
    status: str
    assigned_to: Optional[InternalTaskUserRef] = None
    created_by: Optional[InternalTaskUserRef] = None
    due_date: Optional[date] = None
    is_overdue: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    # What the current viewer may do on this task
    can_update_status: bool = False
    can_edit: bool = False
    can_reassign: bool = False


class InternalTaskSummary(BaseModel):
    total: int = 0
    pending: int = 0
    in_progress: int = 0
    completed: int = 0
    cancelled: int = 0


class InternalTaskCapabilities(BaseModel):
    can_create: bool = False
    can_assign: bool = False
    is_manager: bool = False
    scope: Optional[str] = None


class InternalTaskListResponse(BaseModel):
    items: List[InternalTaskRead]
    total: int
    summary: InternalTaskSummary
    capabilities: InternalTaskCapabilities


class InternalTaskMessageRead(BaseModel):
    message_id: uuid.UUID
    task_id: uuid.UUID
    author_user_id: Optional[uuid.UUID] = None
    author_name: Optional[str] = None
    author_employee_code: Optional[str] = None
    author_department_name: Optional[str] = None
    message_type: str
    message_text: str
    is_own: bool = False
    created_at: datetime


class InternalTaskThreadResponse(BaseModel):
    task: InternalTaskRead
    messages: List[InternalTaskMessageRead]
    can_post: bool = True
