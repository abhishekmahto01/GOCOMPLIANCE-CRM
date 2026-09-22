"""Operations service layer handling task assignment, reassignment, status transitions, and documents."""
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.services import permissions

# Allowed forward status transitions map
VALID_STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "UNASSIGNED": ["ASSIGNED", "CANCELLED"],
    "ASSIGNED": ["IN_PROGRESS", "UNASSIGNED", "CANCELLED"],
    "IN_PROGRESS": ["PENDING_DOCUMENTS", "READY_FOR_SUBMISSION", "SUBMITTED", "CANCELLED"],
    "PENDING_DOCUMENTS": ["IN_PROGRESS", "READY_FOR_SUBMISSION", "CANCELLED"],
    "READY_FOR_SUBMISSION": ["SUBMITTED", "IN_PROGRESS", "CANCELLED"],
    "SUBMITTED": ["AUTHORITY_QUERY", "APPROVED", "CANCELLED"],
    "AUTHORITY_QUERY": ["SUBMITTED", "IN_PROGRESS", "CANCELLED"],
    "APPROVED": [],
    "CANCELLED": [],
}


class ApplicationNotFoundError(Exception):
    """Raised when application is not found."""
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid state transition is requested."""
    pass


class AssignmentAuthorizationError(Exception):
    """Raised when a user is not authorized to assign or reassign tasks."""
    pass


def assign_task(
    session: Session,
    application_id: uuid.UUID,
    assignee_user_id: uuid.UUID,
    assigned_by: User,
    priority: str = "MEDIUM",
    target_due_date: Optional[date] = None,
    notes: Optional[str] = None,
) -> OperationApplication:
    """Assign an unassigned or existing application to an operations employee."""
    app = session.get(OperationApplication, application_id)
    if not app:
        raise ApplicationNotFoundError(f"Operation application with ID '{application_id}' not found.")

    assignee = session.get(User, assignee_user_id)
    if not assignee or assignee.account_status != "ACTIVE":
        raise ValueError(f"Target assignee with ID '{assignee_user_id}' is not an active employee.")

    # Validate assignee belongs to the same company
    if assignee.company_id != app.company_id:
        raise ValueError("Assignee does not belong to the application's company.")

    prev_assignee_id = app.assigned_to_user_id
    now_utc = datetime.now(timezone.utc)

    # Update application
    app.assigned_to_user_id = assignee_user_id
    app.assigned_by_user_id = assigned_by.user_id
    app.assigned_at = now_utc
    app.priority = priority
    if target_due_date:
        app.target_due_date = target_due_date
    if notes:
        app.assignment_notes = notes

    if app.application_status == "UNASSIGNED":
        app.application_status = "ASSIGNED"

    # Log assignment history
    history = ApplicationAssignmentHistory(
        application_id=app.application_id,
        assigned_by_user_id=assigned_by.user_id,
        previous_assignee_user_id=prev_assignee_id,
        new_assignee_user_id=assignee_user_id,
        reason=notes or "Initial task assignment",
        assigned_at=now_utc,
    )
    session.add(history)

    # Log activity
    activity = ApplicationActivityLog(
        application_id=app.application_id,
        actor_user_id=assigned_by.user_id,
        action_type="ASSIGNMENT_CHANGE",
        old_value=str(prev_assignee_id) if prev_assignee_id else "UNASSIGNED",
        new_value=f"{assignee.first_name} {assignee.last_name} ({assignee.employee_code})",
        comment=f"Assigned to {assignee.first_name} {assignee.last_name}. Priority: {priority}",
    )
    session.add(activity)
    session.flush()

    return app


def reassign_task(
    session: Session,
    application_id: uuid.UUID,
    new_assignee_user_id: uuid.UUID,
    reason: str,
    reassigned_by: User,
    priority: Optional[str] = None,
    target_due_date: Optional[date] = None,
) -> OperationApplication:
    """Reassign an existing assigned application to a different operations employee."""
    app = session.get(OperationApplication, application_id)
    if not app:
        raise ApplicationNotFoundError(f"Operation application with ID '{application_id}' not found.")

    new_assignee = session.get(User, new_assignee_user_id)
    if not new_assignee or new_assignee.account_status != "ACTIVE":
        raise ValueError(f"Target assignee with ID '{new_assignee_user_id}' is not an active employee.")

    if new_assignee.company_id != app.company_id:
        raise ValueError("Assignee does not belong to the application's company.")

    prev_assignee_id = app.assigned_to_user_id
    now_utc = datetime.now(timezone.utc)

    app.assigned_to_user_id = new_assignee_user_id
    app.assigned_by_user_id = reassigned_by.user_id
    app.assigned_at = now_utc
    if priority:
        app.priority = priority
    if target_due_date:
        app.target_due_date = target_due_date

    # Log assignment history
    history = ApplicationAssignmentHistory(
        application_id=app.application_id,
        assigned_by_user_id=reassigned_by.user_id,
        previous_assignee_user_id=prev_assignee_id,
        new_assignee_user_id=new_assignee_user_id,
        reason=reason,
        assigned_at=now_utc,
    )
    session.add(history)

    # Log activity
    activity = ApplicationActivityLog(
        application_id=app.application_id,
        actor_user_id=reassigned_by.user_id,
        action_type="ASSIGNMENT_CHANGE",
        old_value=str(prev_assignee_id) if prev_assignee_id else "UNASSIGNED",
        new_value=f"{new_assignee.first_name} {new_assignee.last_name} ({new_assignee.employee_code})",
        comment=f"Reassigned to {new_assignee.first_name} {new_assignee.last_name}. Reason: {reason}",
    )
    session.add(activity)
    session.flush()

    return app


def update_application_status(
    session: Session,
    application_id: uuid.UUID,
    new_status: str,
    actor: User,
    comment: Optional[str] = None,
) -> OperationApplication:
    """Transition application status validating state machine rules."""
    app = session.get(OperationApplication, application_id)
    if not app:
        raise ApplicationNotFoundError(f"Operation application with ID '{application_id}' not found.")

    old_status = app.application_status
    if old_status == new_status:
        return app

    # Validate transition
    allowed = VALID_STATUS_TRANSITIONS.get(old_status, [])
    if new_status not in allowed:
        raise InvalidStatusTransitionError(
            f"Cannot transition application from '{old_status}' to '{new_status}'. Allowed transitions: {allowed}"
        )

    now_utc = datetime.now(timezone.utc)
    app.application_status = new_status
    if new_status == "APPROVED":
        app.completion_date = date.today()

    activity = ApplicationActivityLog(
        application_id=app.application_id,
        actor_user_id=actor.user_id,
        action_type="STATUS_CHANGE",
        old_value=old_status,
        new_value=new_status,
        comment=comment or f"Status changed from {old_status} to {new_status}",
        created_at=now_utc,
    )
    session.add(activity)
    session.flush()

    return app


def update_document_status(
    session: Session,
    app_doc_id: uuid.UUID,
    new_status: str,
    actor: User,
    rejection_reason: Optional[str] = None,
) -> ApplicationDocument:
    """Update document checklist item verification status."""
    doc = session.get(ApplicationDocument, app_doc_id)
    if not doc:
        raise ValueError(f"Application document with ID '{app_doc_id}' not found.")

    old_status = doc.status
    doc.status = new_status
    if new_status == "VERIFIED":
        doc.verified_by_user_id = actor.user_id
        doc.verified_at = datetime.now(timezone.utc)
        doc.rejection_reason = None
    elif new_status == "REJECTED":
        doc.rejection_reason = rejection_reason
        doc.verified_by_user_id = actor.user_id
        doc.verified_at = datetime.now(timezone.utc)
    else:
        doc.verified_by_user_id = None
        doc.verified_at = None

    activity = ApplicationActivityLog(
        application_id=doc.application_id,
        actor_user_id=actor.user_id,
        action_type="DOCUMENT_STATUS_CHANGE",
        old_value=f"{doc.document_code}: {old_status}",
        new_value=f"{doc.document_code}: {new_status}",
        comment=rejection_reason if new_status == "REJECTED" else f"Document '{doc.document_name}' marked as {new_status}",
    )
    session.add(activity)
    session.flush()

    return doc
