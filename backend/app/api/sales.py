"""FastAPI router for Sales Dashboard, Sales Register, Entry Form, and Analytics."""
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.schemas.sales_dashboard import SalesDashboardResponse
from app.schemas.sales_order import (
    SalesEmployeeOption,
    SalesFormOptionsResponse,
    SalesOrderAssignRequest,
    SalesOrderConfirmResponse,
    SalesOrderCreate,
    SalesOrderDetailRead,
    SalesOrderRead,
    SalesOrderUpdate,
    SalesRegisterResponse,
)
from app.services import operation_service, permissions, sales_service

router = APIRouter(prefix="/sales", tags=["Sales Dashboard, Register & Orders"])


@router.get(
    "/dashboard",
    response_model=SalesDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Sales Dashboard Analytics",
    description="Retrieve live calculated KPIs, charts, team performance, and recent orders scoped by user permissions.",
    dependencies=[Depends(require_module_permission("SALES_DASHBOARD", "view"))],
)
def get_sales_dashboard(
    preset: Optional[str] = Query("this_month", description="Preset range: today, this_week, this_month, this_quarter, this_year, custom"),
    from_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD) for custom range"),
    to_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD) for custom range"),
    employee_id: Optional[uuid.UUID] = Query(None, description="Filter by salesperson employee ID"),
    service_id: Optional[uuid.UUID] = Query(None, description="Filter by service ID"),
    lead_source: Optional[str] = Query(None, description="Filter by lead source (WEBSITE, REFERRAL, DIRECT, OTHERS)"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status (FULLY_PAID, PARTIALLY_PAID, PENDING, OVERDUE)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesDashboardResponse:
    return sales_service.get_sales_dashboard_data(
        session=session,
        current_user=current_user,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        payment_status=payment_status,
    )


@router.get(
    "/dashboard/export",
    status_code=status.HTTP_200_OK,
    summary="Export Sales Dashboard Report",
    description="Export filtered sales orders as a downloadable CSV file scoped to user permissions.",
    dependencies=[Depends(require_module_permission("SALES_DASHBOARD", "export"))],
)
def export_sales_dashboard(
    preset: Optional[str] = Query("this_month", description="Preset range"),
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    employee_id: Optional[uuid.UUID] = Query(None, description="Filter by employee"),
    service_id: Optional[uuid.UUID] = Query(None, description="Filter by service"),
    lead_source: Optional[str] = Query(None, description="Filter by lead source"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    """Generate and stream CSV export for dashboard."""
    csv_content, filename = sales_service.export_sales_orders_csv(
        session=session,
        current_user=current_user,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        payment_status=payment_status,
    )
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@router.get(
    "/form-options",
    response_model=SalesFormOptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Sales Entry Form Options",
    description="Retrieve services, salespersons scoped to user RBAC, clients list, and lead sources for form dropdowns.",
    dependencies=[Depends(require_module_permission("SALES_CONFIRMED_ORDER", "read"))],
)
def get_sales_form_options(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesFormOptionsResponse:
    """Return form dropdown options scoped by user permissions."""
    return sales_service.get_sales_form_options(session=session, current_user=current_user)


@router.get(
    "/register",
    response_model=SalesRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Sales Register Table Data",
    description="Retrieve paginated, searchable, filtered sales register entries covering all 20 columns.",
    dependencies=[Depends(require_module_permission("SALES_MY_ORDERS", "read"))],
)
def get_sales_register(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(25, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search across client name, contact, order/invoice numbers, notes"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    work_status: Optional[str] = Query(None, description="Filter by work / application status"),
    employee_id: Optional[uuid.UUID] = Query(None, description="Filter by salesperson employee ID"),
    service_id: Optional[uuid.UUID] = Query(None, description="Filter by service ID"),
    lead_source: Optional[str] = Query(None, description="Filter by lead source"),
    from_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_by: str = Query("order_date", description="Sort column"),
    sort_dir: str = Query("desc", description="Sort direction (asc/desc)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesRegisterResponse:
    """Return paginated Sales Register records with summary statistics."""
    return sales_service.get_sales_register_data(
        session=session,
        current_user=current_user,
        page=page,
        limit=limit,
        search=search,
        payment_status=payment_status,
        work_status=work_status,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        from_date=from_date,
        to_date=to_date,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get(
    "/register/export",
    status_code=status.HTTP_200_OK,
    summary="Export Sales Register CSV",
    description="Export full Sales Register dataset matching all 20 columns in the director's order.",
    dependencies=[Depends(require_module_permission("SALES_MY_ORDERS", "export"))],
)
def export_sales_register(
    search: Optional[str] = Query(None, description="Search query"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    work_status: Optional[str] = Query(None, description="Filter by work status"),
    employee_id: Optional[uuid.UUID] = Query(None, description="Filter by employee"),
    service_id: Optional[uuid.UUID] = Query(None, description="Filter by service"),
    lead_source: Optional[str] = Query(None, description="Filter by lead source"),
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
):
    """Generate and stream 20-column CSV export."""
    csv_content, filename = sales_service.export_sales_register_csv(
        session=session,
        current_user=current_user,
        search=search,
        payment_status=payment_status,
        work_status=work_status,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        from_date=from_date,
        to_date=to_date,
    )
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@router.get(
    "/orders",
    response_model=List[SalesOrderDetailRead],
    status_code=status.HTTP_200_OK,
    summary="List Sales Orders",
    description="Retrieve sales orders within user data scope with pagination and filtering.",
    dependencies=[Depends(require_module_permission("SALES_MY_ORDERS", "read"))],
)
def list_sales_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    employee_id: Optional[uuid.UUID] = Query(None),
    service_id: Optional[uuid.UUID] = Query(None),
    payment_status: Optional[str] = Query(None),
    confirmation_status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[SalesOrderDetailRead]:
    """Return list of sales orders within data scope."""
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_MY_ORDERS")
    if scope_ctx.scope == "SELF":
        employee_id = current_user.user_id

    query = sales_service._apply_sales_filters(
        session.query(SalesOrder),
        scope_ctx=scope_ctx,
        employee_id=employee_id,
        service_id=service_id,
        payment_status=payment_status,
    )
    if confirmation_status:
        query = query.filter(SalesOrder.confirmation_status == confirmation_status.upper())

    orders = query.order_by(SalesOrder.order_date.desc(), SalesOrder.created_at.desc()).offset(skip).limit(limit).all()

    result: List[SalesOrderDetailRead] = []
    for idx, o in enumerate(orders):
        c_name = o.client.client_name if o.client else "Client"
        c_phone = o.client.contact_phone if o.client else ""
        s_name = o.service.service_name if o.service else "Service"
        s_code = o.service.service_code if o.service else ""
        sp_name = f"{o.salesperson.first_name} {o.salesperson.last_name}".strip() if o.salesperson else "Rep"
        sp_code = o.salesperson.employee_code if o.salesperson else ""
        app_id = o.application.application_id if o.application else None
        app_num = o.application.application_number if o.application else None
        op_st = o.application.application_status if o.application else o.confirmation_status
        assigned_to_id = o.application.assigned_to_user_id if o.application else None
        assigned_to_name = (
            f"{o.application.assigned_to.first_name} {o.application.assigned_to.last_name}".strip()
            if (o.application and o.application.assigned_to)
            else "Unassigned"
        )
        assigned_to_code = (
            o.application.assigned_to.employee_code
            if (o.application and o.application.assigned_to)
            else None
        )

        result.append(
            SalesOrderDetailRead(
                s_no=skip + idx + 1,
                order_id=o.order_id,
                order_number=o.order_number,
                company_id=o.company_id,
                client_id=o.client_id,
                service_id=o.service_id,
                salesperson_user_id=o.salesperson_user_id,
                lead_source=o.lead_source,
                order_date=o.order_date,
                formatted_date=o.order_date.strftime("%d %b %Y"),
                order_value=o.order_value,
                amount_received=o.amount_received,
                balance_amount=o.balance_amount,
                govt_fees=o.govt_fees,
                incidental_cost=o.incidental_cost,
                profit_amount=o.profit_amount,
                payment_status=o.payment_status,
                confirmation_status=o.confirmation_status,
                confirmed_at=o.confirmed_at,
                proforma_invoice_no=o.proforma_invoice_no,
                tax_invoice_no=o.tax_invoice_no,
                reimbursement_note=o.reimbursement_note,
                notes=o.notes,
                remarks=o.notes,
                created_at=o.created_at,
                updated_at=o.updated_at,
                client_name=c_name,
                contact_no=c_phone,
                service_name=s_name,
                service_code=s_code,
                salesperson_name=sp_name,
                salesperson_code=sp_code,
                assigned_to_user_id=assigned_to_id,
                assigned_to_name=assigned_to_name,
                assigned_to_code=assigned_to_code,
                work_status=op_st,
                application_id=app_id,
                application_number=app_num,
                operation_status=op_st,
            )
        )
    return result


@router.post(
    "/orders",
    response_model=SalesOrderDetailRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Sales Order",
    description="Create a new sales order with client matching, RBAC scoping, and financial calculations.",
    dependencies=[Depends(require_module_permission("SALES_CONFIRMED_ORDER", "write"))],
)
def create_order(
    data: SalesOrderCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesOrderDetailRead:
    """Create a new sales order."""
    try:
        order = sales_service.create_sales_order(session, data, current_user)
        session.commit()
        session.refresh(order)

        c_name = order.client.client_name if order.client else "Client"
        c_phone = order.client.contact_phone if order.client else ""
        s_name = order.service.service_name if order.service else "Service"
        sp_name = f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "Rep"
        app_id = order.application.application_id if order.application else None
        app_num = order.application.application_number if order.application else None
        op_st = order.application.application_status if order.application else order.confirmation_status
        assigned_to_id = order.application.assigned_to_user_id if order.application else None
        assigned_to_name = (
            f"{order.application.assigned_to.first_name} {order.application.assigned_to.last_name}".strip()
            if (order.application and order.application.assigned_to)
            else "Unassigned"
        )

        return SalesOrderDetailRead(
            s_no=1,
            order_id=order.order_id,
            order_number=order.order_number,
            company_id=order.company_id,
            client_id=order.client_id,
            service_id=order.service_id,
            salesperson_user_id=order.salesperson_user_id,
            lead_source=order.lead_source,
            order_date=order.order_date,
            formatted_date=order.order_date.strftime("%d %b %Y"),
            order_value=order.order_value,
            amount_received=order.amount_received,
            balance_amount=order.balance_amount,
            govt_fees=order.govt_fees,
            incidental_cost=order.incidental_cost,
            profit_amount=order.profit_amount,
            payment_status=order.payment_status,
            confirmation_status=order.confirmation_status,
            confirmed_at=order.confirmed_at,
            proforma_invoice_no=order.proforma_invoice_no,
            tax_invoice_no=order.tax_invoice_no,
            reimbursement_note=order.reimbursement_note,
            notes=order.notes,
            remarks=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            client_name=c_name,
            contact_no=c_phone,
            service_name=s_name,
            salesperson_name=sp_name,
            assigned_to_user_id=assigned_to_id,
            assigned_to_name=assigned_to_name,
            work_status=op_st,
            application_id=app_id,
            application_number=app_num,
            operation_status=op_st,
        )
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/orders/{order_id}",
    response_model=SalesOrderDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Get Sales Order Details",
    description="Retrieve full details for a single sales order within data scope.",
    dependencies=[Depends(require_module_permission("SALES_MY_ORDERS", "read"))],
)
def get_order_detail(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesOrderDetailRead:
    """Get single sales order details."""
    order = session.get(SalesOrder, order_id)
    if not order or order.confirmation_status == "CANCELLED":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found.")

    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_MY_ORDERS")
    if not scope_ctx.is_user_permitted(order.salesperson_user_id, order.company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this sales order.")

    c_name = order.client.client_name if order.client else "Client"
    c_phone = order.client.contact_phone if order.client else ""
    s_name = order.service.service_name if order.service else "Service"
    sp_name = f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "Rep"
    app_id = order.application.application_id if order.application else None
    app_num = order.application.application_number if order.application else None
    op_st = order.application.application_status if order.application else order.confirmation_status
    assigned_to_id = order.application.assigned_to_user_id if order.application else None
    assigned_to_name = (
        f"{order.application.assigned_to.first_name} {order.application.assigned_to.last_name}".strip()
        if (order.application and order.application.assigned_to)
        else "Unassigned"
    )

    return SalesOrderDetailRead(
        order_id=order.order_id,
        order_number=order.order_number,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        salesperson_user_id=order.salesperson_user_id,
        lead_source=order.lead_source,
        order_date=order.order_date,
        formatted_date=order.order_date.strftime("%d %b %Y"),
        order_value=order.order_value,
        amount_received=order.amount_received,
        balance_amount=order.balance_amount,
        govt_fees=order.govt_fees,
        incidental_cost=order.incidental_cost,
        profit_amount=order.profit_amount,
        payment_status=order.payment_status,
        confirmation_status=order.confirmation_status,
        confirmed_at=order.confirmed_at,
        proforma_invoice_no=order.proforma_invoice_no,
        tax_invoice_no=order.tax_invoice_no,
        reimbursement_note=order.reimbursement_note,
        notes=order.notes,
        remarks=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
        client_name=c_name,
        contact_no=c_phone,
        service_name=s_name,
        salesperson_name=sp_name,
        assigned_to_user_id=assigned_to_id,
        assigned_to_name=assigned_to_name,
        work_status=op_st,
        application_id=app_id,
        application_number=app_num,
        operation_status=op_st,
    )


@router.put(
    "/orders/{order_id}",
    response_model=SalesOrderDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Update Sales Order",
    description="Update existing sales order financial and sales fields with permission verification and calculation updates.",
    dependencies=[Depends(require_module_permission("SALES_MY_ORDERS", "update"))],
)
def update_order(
    order_id: uuid.UUID,
    data: SalesOrderUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesOrderDetailRead:
    """Update sales order details."""
    try:
        result = sales_service.update_sales_order(session, order_id, data, current_user)
        session.commit()
        return result
    except sales_service.SalesOrderNotFoundError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (sales_service.SalesOrderPermissionError, permissions.PermissionDeniedError) as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.delete(
    "/orders/{order_id}",
    response_model=SalesOrderDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Delete Sales Order",
    description="Safely soft-delete a sales entry and remove linked Operations task if not completed.",
    dependencies=[Depends(require_module_permission("SALES_MY_ORDERS", "delete"))],
)
def delete_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesOrderDetailRead:
    """Delete a sales order and cancel linked operations application atomically."""
    try:
        result = sales_service.delete_sales_order(session, order_id, current_user)
        session.commit()
        return result
    except sales_service.SalesOrderNotFoundError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (sales_service.SalesOrderPermissionError, permissions.PermissionDeniedError) as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except sales_service.SalesOrderDeletionError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "/orders/{order_id}/confirm",
    response_model=SalesOrderConfirmResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm Sales Order and Hand Over to Operations",
    description="Transition order to CONFIRMED and automatically create unassigned Operations application.",
    dependencies=[Depends(require_module_permission("SALES_CONFIRMED_ORDER", "update"))],
)
def confirm_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesOrderConfirmResponse:
    """Confirm order and hand over to operations."""
    try:
        result = sales_service.confirm_sales_order(session, order_id, current_user)
        session.commit()
        return result
    except sales_service.SalesOrderNotFoundError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found.")


@router.get(
    "/operations-assignees",
    response_model=List[SalesEmployeeOption],
    status_code=status.HTTP_200_OK,
    summary="Get Eligible Operations Assignees",
    description="Retrieve list of active Operations team members available for task assignment.",
    dependencies=[Depends(require_module_permission("SALES_MY_ORDERS", "read"))],
)
def get_operations_assignees(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[SalesEmployeeOption]:
    """Return active Operations department employees eligible for task assignment."""
    return sales_service.get_eligible_operations_assignees(session, current_user.company_id)


@router.post(
    "/orders/{order_id}/assign",
    response_model=SalesOrderDetailRead,
    status_code=status.HTTP_200_OK,
    summary="Assign Operations Work to Team Member",
    description="Assign or reassign an order's operations application to an eligible Operations team member. Authorized Operations managers only.",
)
def assign_order_operations(
    order_id: uuid.UUID,
    data: SalesOrderAssignRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesOrderDetailRead:
    """Assign order work to an Operations team member."""
    try:
        result = sales_service.assign_sales_order_operations(
            session=session,
            order_id=order_id,
            assignee_user_id=data.assignee_user_id,
            assigned_by=current_user,
            priority=data.priority or "MEDIUM",
            target_due_date=data.target_due_date,
            notes=data.notes,
        )
        session.commit()
        return result
    except sales_service.SalesOrderNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (sales_service.SalesOrderPermissionError, permissions.PermissionDeniedError, operation_service.AssignmentAuthorizationError) as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
