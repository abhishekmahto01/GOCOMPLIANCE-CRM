"""FastAPI router for Operations Dashboard, Task Assignment, My Tasks, and Application Life Cycle."""
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_fully_activated_user, require_module_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.operation_application import (
    ApplicationDocRead,
    ApplicationDocUpdate,
    ApplicationStatusUpdateRequest,
    OperationApplicationDetailRead,
    OperationApplicationRead,
    OperationRemarkCreate,
    OperationRemarkRead,
    OperationsDashboardResponse,
    OperationsTaskListResponse,
    TaskAssignRequest,
    TaskReassignRequest,
)
from app.schemas.sales_order import SalesEmployeeOption
from app.services import operation_service, permissions

router = APIRouter(prefix="/operations", tags=["Operations Tasks & Workspace"])


@router.get(
    "/dashboard",
    response_model=OperationsDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Operations Dashboard Analytics",
    description="Retrieve live calculated KPIs, status distribution, executive workload, and priority queue scoped to user permissions.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def get_operations_dashboard(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationsDashboardResponse:
    try:
        return operation_service.get_operations_dashboard_data(
            session=session,
            user=current_user,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/tasks",
    response_model=OperationsTaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Operations Tasks",
    description="Retrieve filtered and paginated operation applications scoped to user permissions.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def list_operations_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter or OVERDUE"),
    priority: Optional[str] = Query(None, description="Priority filter: LOW, MEDIUM, HIGH, URGENT"),
    search: Optional[str] = Query(None, description="Search term for client, service, application, or order number"),
    assigned_to_user_id: Optional[uuid.UUID] = Query(None, description="Filter by assigned employee user ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Sort field: created_at, application_number, target_due_date, priority, application_status"),
    sort_order: str = Query("desc", description="Sort direction: asc or desc"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationsTaskListResponse:
    try:
        return operation_service.get_operations_tasks(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            status=status_filter,
            priority=priority,
            search=search,
            assigned_to_user_id=assigned_to_user_id,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/tasks/my-tasks",
    response_model=OperationsTaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get My Assigned Operations Tasks",
    description="Retrieve tasks assigned strictly to the authenticated employee.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def list_my_assigned_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter"),
    priority: Optional[str] = Query(None, description="Priority filter"),
    search: Optional[str] = Query(None, description="Search term"),
    assigned_to_user_id: Optional[uuid.UUID] = Query(None, description="Filter by specific assignee"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationsTaskListResponse:
    try:
        return operation_service.get_my_tasks(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            status=status_filter,
            priority=priority,
            search=search,
            assigned_to_user_id=assigned_to_user_id,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/tasks/unassigned",
    response_model=OperationsTaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Unassigned Applications",
    description="Retrieve unassigned applications awaiting assignment to an operations employee.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def list_unassigned_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationsTaskListResponse:
    try:
        return operation_service.get_unassigned_operations_orders(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/tasks/{application_id}",
    response_model=OperationApplicationDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Get Task Details",
    description="Retrieve full details, document checklist, assignment history, and activity timeline for an application.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def get_task_detail(
    application_id: uuid.UUID,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationApplicationDetailRead:
    try:
        return operation_service.get_operation_application_detail(
            session=session,
            application_id=application_id,
            user=current_user,
        )
    except operation_service.ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/tasks/{application_id}/assign",
    response_model=OperationApplicationDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Assign Task to Operations Employee",
    description="Assign an unassigned or existing task to an operations employee.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "assign"))],
)
def assign_application_task(
    application_id: uuid.UUID,
    payload: TaskAssignRequest,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationApplicationDetailRead:
    try:
        operation_service.assign_task(
            session=session,
            application_id=application_id,
            assignee_user_id=payload.assignee_user_id,
            assigned_by=current_user,
            priority=payload.priority or "MEDIUM",
            target_due_date=payload.target_due_date,
            notes=payload.notes,
        )
        session.commit()
        return operation_service.get_operation_application_detail(
            session=session,
            application_id=application_id,
            user=current_user,
        )
    except operation_service.ApplicationNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValueError, operation_service.AssignmentAuthorizationError) as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/tasks/{application_id}/reassign",
    response_model=OperationApplicationDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Reassign Task to Different Employee",
    description="Reassign an active task to another employee with mandatory audit reason.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "reassign"))],
)
def reassign_application_task(
    application_id: uuid.UUID,
    payload: TaskReassignRequest,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationApplicationDetailRead:
    try:
        operation_service.reassign_task(
            session=session,
            application_id=application_id,
            new_assignee_user_id=payload.new_assignee_user_id,
            reason=payload.reason,
            reassigned_by=current_user,
            priority=payload.priority,
            target_due_date=payload.target_due_date,
        )
        session.commit()
        return operation_service.get_operation_application_detail(
            session=session,
            application_id=application_id,
            user=current_user,
        )
    except operation_service.ApplicationNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValueError, operation_service.AssignmentAuthorizationError) as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/tasks/{application_id}/status",
    response_model=OperationApplicationDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Update Application Status",
    description="Advance or transition application lifecycle status adhering to allowed state transitions.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "edit"))],
)
def update_application_status(
    application_id: uuid.UUID,
    payload: ApplicationStatusUpdateRequest,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationApplicationDetailRead:
    try:
        operation_service.update_application_status(
            session=session,
            application_id=application_id,
            new_status=payload.new_status,
            actor=current_user,
            comment=payload.comment,
        )
        session.commit()
        return operation_service.get_operation_application_detail(
            session=session,
            application_id=application_id,
            user=current_user,
        )
    except operation_service.ApplicationNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except operation_service.InvalidStatusTransitionError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/tasks/documents/{app_doc_id}/status",
    response_model=ApplicationDocRead,
    status_code=status.HTTP_200_OK,
    summary="Update Document Checklist Status",
    description="Verify, reject, or mark a required application document as received.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "edit"))],
)
def update_document_status(
    app_doc_id: uuid.UUID,
    payload: ApplicationDocUpdate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> ApplicationDocRead:
    try:
        doc = operation_service.update_document_status(
            session=session,
            app_doc_id=app_doc_id,
            new_status=payload.status,
            actor=current_user,
            rejection_reason=payload.rejection_reason,
        )
        session.commit()
        v_name = f"{current_user.first_name} {current_user.last_name}".strip() if doc.verified_by_user_id else None
        return ApplicationDocRead(
            app_doc_id=doc.app_doc_id,
            application_id=doc.application_id,
            document_code=doc.document_code,
            document_name=doc.document_name,
            is_mandatory=doc.is_mandatory,
            status=doc.status,
            rejection_reason=doc.rejection_reason,
            verified_by_user_id=doc.verified_by_user_id,
            verified_by_name=v_name,
            verified_at=doc.verified_at,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/assignees",
    response_model=List[SalesEmployeeOption],
    status_code=status.HTTP_200_OK,
    summary="List Eligible Operations Assignees",
    description="Retrieve list of active Operations team members who can be assigned tasks.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def list_operations_assignees(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> List[SalesEmployeeOption]:
    users = operation_service.get_eligible_operations_assignees(session=session, user=current_user)
    return [
        SalesEmployeeOption(
            user_id=u.user_id,
            employee_code=u.employee_code,
            full_name=f"{u.first_name} {u.last_name}".strip(),
            department_name=u.department.department_name if u.department else None,
            designation_name=u.designation.designation_name if u.designation else None,
        )
        for u in users
    ]


@router.post(
    "/tasks/{application_id}/remarks",
    response_model=OperationRemarkRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add Operations Remark to Task",
    description="Add a chronological remark regarding delay reasons, blockers, or statutory follow-ups to an assigned task.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def add_operation_remark(
    application_id: uuid.UUID,
    payload: OperationRemarkCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OperationRemarkRead:
    try:
        remark = operation_service.add_operation_remark(
            session=session,
            application_id=application_id,
            remark_text=payload.remark_text,
            author=current_user,
        )
        session.commit()
        session.refresh(remark)
        return operation_service._to_remark_read(remark)
    except operation_service.ApplicationNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/tasks/{application_id}/remarks",
    response_model=List[OperationRemarkRead],
    status_code=status.HTTP_200_OK,
    summary="Get Operations Remarks History",
    description="Retrieve all chronological remarks recorded on the task.",
    dependencies=[Depends(require_module_permission("OPERATIONS", "view"))],
)
def list_operation_remarks(
    application_id: uuid.UUID,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> List[OperationRemarkRead]:
    try:
        return operation_service.get_operation_remarks(
            session=session,
            application_id=application_id,
            user=current_user,
        )
    except operation_service.ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

