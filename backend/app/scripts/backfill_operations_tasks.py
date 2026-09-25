"""Idempotent Safe Backfill Script for Missing Operations Tasks in GOCOMPLIANCE CRM.

Compares confirmed Sales Orders with Operations Applications and creates missing
task records without modifying, overwriting, or deleting any existing records.

Usage:
    # Dry-run inspection (default, read-only)
    python -m app.scripts.backfill_operations_tasks --dry-run

    # Execute backfill
    python -m app.scripts.backfill_operations_tasks --execute
"""
import argparse
import sys
import uuid
from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.department import Department
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.models.user import User
from app.services.sales_service import generate_application_number


def inspect_and_backfill(session: Session, dry_run: bool = True) -> Tuple[int, int, List[dict]]:
    """Scan all confirmed sales orders and create missing operation applications safely."""
    # 1. Fetch all confirmed sales orders
    orders_stmt = (
        select(SalesOrder)
        .where(SalesOrder.confirmation_status == "CONFIRMED")
        .order_by(SalesOrder.order_date.asc(), SalesOrder.created_at.asc())
    )
    orders = session.execute(orders_stmt).scalars().all()

    total_orders = len(orders)
    missing_records: List[dict] = []
    created_count = 0

    for order in orders:
        # Check if OperationApplication already exists
        existing_app = session.execute(
            select(OperationApplication).where(OperationApplication.sales_order_id == order.order_id)
        ).scalar_one_or_none()

        if existing_app:
            continue

        c_name = order.client.client_name if order.client else "Unknown Client"
        s_name = order.service.service_name if order.service else "Unknown Service"
        sp_name = (
            f"{order.salesperson.first_name} {order.salesperson.last_name}".strip()
            if order.salesperson
            else "Unknown Salesperson"
        )

        missing_records.append({
            "order_id": order.order_id,
            "order_number": order.order_number,
            "order_date": order.order_date,
            "client_name": c_name,
            "service_name": s_name,
            "salesperson_name": sp_name,
            "company_id": order.company_id,
        })

    if dry_run:
        return total_orders, len(missing_records), missing_records

    # Execute creation for missing records
    now_utc = datetime.now(timezone.utc)
    for item in missing_records:
        order = session.get(SalesOrder, item["order_id"])
        if not order:
            continue

        # Look up eligible default Operations assignee (Mansi Singhal CG0003 or first active Ops member)
        assigned_target = session.execute(
            select(User)
            .outerjoin(Department, User.department_id == Department.department_id)
            .where(
                User.company_id == order.company_id,
                User.account_status == "ACTIVE",
                or_(
                    User.employee_code == "CG0003",
                    User.first_name.ilike("%mansi%"),
                    Department.department_code.in_(["OP", "OPS", "OPERATIONS"]),
                    Department.department_name.ilike("%operation%"),
                ),
            )
            .order_by(
                case(
                    (User.employee_code == "CG0003", 0),
                    (User.first_name.ilike("%mansi%"), 1),
                    else_=2,
                ),
                User.created_at.asc(),
            )
        ).scalars().first()

        assigned_to_id = assigned_target.user_id if assigned_target else None
        assigned_by_id = order.salesperson_user_id or (assigned_target.user_id if assigned_target else None)
        app_status = "ASSIGNED" if assigned_target else "UNASSIGNED"
        app_num = generate_application_number(session, order.order_date)

        new_app = OperationApplication(
            application_number=app_num,
            sales_order_id=order.order_id,
            company_id=order.company_id,
            client_id=order.client_id,
            service_id=order.service_id,
            assigned_to_user_id=assigned_to_id,
            assigned_by_user_id=assigned_by_id,
            assigned_at=now_utc if assigned_target else None,
            priority="MEDIUM",
            application_status=app_status,
            target_due_date=None,
            assignment_notes=order.notes,
        )
        session.add(new_app)
        session.flush()

        # Add checklist documents
        required_docs = session.execute(
            select(ServiceRequiredDocument)
            .where(ServiceRequiredDocument.service_id == order.service_id)
            .order_by(ServiceRequiredDocument.display_order.asc())
        ).scalars().all()

        for r_doc in required_docs:
            app_doc = ApplicationDocument(
                application_id=new_app.application_id,
                document_code=r_doc.document_code,
                document_name=r_doc.document_name,
                is_mandatory=r_doc.is_mandatory,
                status="PENDING",
            )
            session.add(app_doc)

        if assigned_target:
            history = ApplicationAssignmentHistory(
                application_id=new_app.application_id,
                assigned_by_user_id=assigned_by_id or assigned_target.user_id,
                previous_assignee_user_id=None,
                new_assignee_user_id=assigned_target.user_id,
                reason="Idempotent backfill assignment for confirmed sales order",
                assigned_at=now_utc,
            )
            session.add(history)

        activity = ApplicationActivityLog(
            application_id=new_app.application_id,
            actor_user_id=assigned_by_id or (assigned_target.user_id if assigned_target else uuid.uuid4()),
            action_type="CREATION",
            old_value="NONE",
            new_value=f"{assigned_target.first_name} {assigned_target.last_name} ({assigned_target.employee_code})" if assigned_target else "UNASSIGNED",
            comment=f"Backfilled application for sales order {order.order_number}.",
            created_at=now_utc,
        )
        session.add(activity)
        session.flush()
        created_count += 1

    session.commit()
    return total_orders, created_count, missing_records


def main():
    parser = argparse.ArgumentParser(description="Safely backfill missing Operations tasks for confirmed Sales orders.")
    parser.add_argument("--execute", action="store_true", help="Execute backfill creation (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run inspection only without committing changes")
    args = parser.parse_args()

    is_dry_run = not args.execute or args.dry_run

    print("=" * 70)
    print("GOCOMPLIANCE CRM - OPERATIONS TASKS SAFE BACKFILL")
    print(f"Mode: {'DRY RUN (READ-ONLY)' if is_dry_run else 'EXECUTE (CREATING MISSING TASKS)'}")
    print("=" * 70)

    session = SessionLocal()
    try:
        total_orders, count, records = inspect_and_backfill(session, dry_run=is_dry_run)
        print(f"Total Confirmed Sales Orders Checked: {total_orders}")
        print(f"Existing Operations Tasks Matched:     {total_orders - len(records)}")
        print(f"Missing Operations Tasks Identified:  {len(records)}")

        if records:
            print("\nMissing Task Details:")
            for idx, r in enumerate(records, 1):
                print(f"  {idx}. Order: {r['order_number']} | Date: {r['order_date']} | Client: {r['client_name']} | Service: {r['service_name']} | Rep: {r['salesperson_name']}")

        if is_dry_run:
            if len(records) == 0:
                print("\nStatus: All confirmed sales orders already have corresponding Operations tasks. No backfill needed.")
            else:
                print(f"\nDry Run Complete: {len(records)} tasks need creation. Run with `--execute` to create them.")
        else:
            print(f"\nExecution Complete: Successfully created {count} Operations tasks.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
