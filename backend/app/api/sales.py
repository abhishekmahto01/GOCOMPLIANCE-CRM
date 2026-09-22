"""FastAPI router for Sales Dashboard, Orders, and Analytics."""
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
    SalesOrderConfirmResponse,
    SalesOrderCreate,
    SalesOrderDetailRead,
    SalesOrderRead,
)
from app.services import permissions, sales_service

router = APIRouter(prefix="/sales", tags=["Sales Dashboard & Orders"])


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
    """Generate and stream CSV export."""
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

    orders = query.order_by(SalesOrder.order_date.desc()).offset(skip).limit(limit).all()

    result: List[SalesOrderDetailRead] = []
    for o in orders:
        c_name = o.client.client_name if o.client else "Client"
        s_name = o.service.service_name if o.service else "Service"
        sp_name = f"{o.salesperson.first_name} {o.salesperson.last_name}" if o.salesperson else "Rep"
        app_id = o.application.application_id if o.application else None
        app_num = o.application.application_number if o.application else None
        op_st = o.application.application_status if o.application else "PENDING"

        result.append(
            SalesOrderDetailRead(
                order_id=o.order_id,
                order_number=o.order_number,
                company_id=o.company_id,
                client_id=o.client_id,
                service_id=o.service_id,
                salesperson_user_id=o.salesperson_user_id,
                lead_source=o.lead_source,
                order_date=o.order_date,
                order_value=o.order_value,
                amount_received=o.amount_received,
                balance_amount=o.balance_amount,
                payment_status=o.payment_status,
                confirmation_status=o.confirmation_status,
                confirmed_at=o.confirmed_at,
                notes=o.notes,
                created_at=o.created_at,
                updated_at=o.updated_at,
                client_name=c_name,
                service_name=s_name,
                salesperson_name=sp_name,
                application_id=app_id,
                application_number=app_num,
                operation_status=op_st,
            )
        )
    return result


@router.post(
    "/orders",
    response_model=SalesOrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Sales Order",
    description="Create a new sales order.",
    dependencies=[Depends(require_module_permission("SALES_CONFIRMED_ORDER", "write"))],
)
def create_order(
    data: SalesOrderCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesOrderRead:
    """Create a new sales order."""
    try:
        order = sales_service.create_sales_order(session, data, current_user)
        session.commit()
        return SalesOrderRead.model_validate(order)
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


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
