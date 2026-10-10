"""Tests for salesperson company enforcement in GOCOMPLIANCE-CRM.

Covers:
1. A Gocompliances salesperson creates a sale without company_id; backend assigns Gocompliances.
2. Supplying another company_id is rejected.
3. A salesperson from another company creates sales for that company.
4. Ordinary salespersons cannot switch companies or access another salesperson's records through filters or direct record IDs.
5. Director/Admin retain permitted all-company access.
6. Ordinary edits cannot change record company.
7. Employee company changes affect new sales only; historical records retain their original company.
8. Missing/inactive employee company blocks creation with clear error message.
9. Cross-company Operations assignment works without changing sale company.
"""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.operation_application import OperationApplication
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.sales_order import SalesOrderCreate, SalesOrderUpdate
from app.services.sales_service import (
    create_sales_order,
    get_sales_register_data,
    update_sales_order,
)


@pytest.fixture
def enforcement_fixture(db_session: Session):
    """Seed test companies, departments, users, and permissions."""
    # 1. Company A: Gocompliances
    comp_a = Company(
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances Private Limited",
        employee_code_prefix="CG",
        status="ACTIVE",
    )
    # 2. Company B: Legal Compliance Corp
    comp_b = Company(
        company_code="LEGALCORP",
        company_name="Legal Compliance Corp",
        employee_code_prefix="LC",
        status="ACTIVE",
    )
    # 3. Company C (Inactive)
    comp_c_inactive = Company(
        company_code="INACTIVE_CORP",
        company_name="Inactive Corp",
        employee_code_prefix="IC",
        status="INACTIVE",
    )
    db_session.add_all([comp_a, comp_b, comp_c_inactive])
    db_session.flush()

    # Departments (Common Masters)
    dept_sales = Department(
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    dept_ops = Department(
        department_code="OPERATIONS",
        department_name="Operations",
        status="ACTIVE",
    )
    dept_admin = Department(
        department_code="ADMINISTRATION",
        department_name="Administration",
        status="ACTIVE",
    )
    db_session.add_all([dept_sales, dept_ops, dept_admin])
    db_session.flush()

    # Designations (Common Masters)
    desig_sales = Designation(
        designation_code="SALES_EXEC",
        designation_name="Sales Executive",
        level_rank=5,
        status="ACTIVE",
    )
    desig_ops = Designation(
        designation_code="OPS_EXEC",
        designation_name="Operations Executive",
        level_rank=5,
        status="ACTIVE",
    )
    desig_dir = Designation(
        designation_code="DIRECTOR",
        designation_name="Director",
        level_rank=1,
        status="ACTIVE",
    )
    db_session.add_all([desig_sales, desig_ops, desig_dir])
    db_session.flush()

    # Service
    service = ServiceMaster(
        service_code="SRV_FSSAI_001",
        service_name="FSSAI Registration",
        category="LICENCE",
        base_price=Decimal("3500.00"),
        govt_fee=Decimal("1500.00"),
        standard_turnaround_days=15,
        status="ACTIVE",
    )
    db_session.add(service)
    db_session.flush()

    # Modules for permissions
    modules = {}
    for code, name in [
        ("SALES", "Sales"),
        ("SALES_REGISTER", "Sales Register"),
        ("SALES_MY_ORDERS", "My Sales Orders"),
        ("SALES_CONFIRMED_ORDER", "Confirmed Sales Orders"),
        ("SALES_DASHBOARD", "Sales Dashboard"),
        ("OPERATIONS", "Operations"),
        ("OPERATIONS_DASHBOARD", "Operations Dashboard"),
    ]:
        mod = Module(
            module_code=code,
            module_name=name,
            route=f"/sales/{code.lower()}",
            is_navigation=True,
            status="ACTIVE",
        )
        db_session.add(mod)
        db_session.flush()
        modules[code] = mod

    # User 1: Karishma (Salesperson at Gocompliances)
    karishma = User(
        employee_code="CG0010",
        company_id=comp_a.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Karishma",
        last_name="Sharma",
        official_email="karishma@gocompliances.in",
        mobile_number="+919811100001",
        date_of_joining=date(2025, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # User 2: Rahul (Salesperson at Gocompliances - Peer of Karishma)
    rahul = User(
        employee_code="CG0011",
        company_id=comp_a.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Rahul",
        last_name="Verma",
        official_email="rahul@gocompliances.in",
        mobile_number="+919811100002",
        date_of_joining=date(2025, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # User 3: Priya (Salesperson at LegalCorp)
    priya = User(
        employee_code="LC0020",
        company_id=comp_b.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Priya",
        last_name="Patel",
        official_email="priya@legalcorp.in",
        mobile_number="+919811100003",
        date_of_joining=date(2025, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # User 4: Admin / Director (Privileged User with ALL scope)
    admin_director = User(
        employee_code="CG0001",
        company_id=comp_a.company_id,
        department_id=dept_admin.department_id,
        designation_id=desig_dir.designation_id,
        first_name="Rajesh",
        last_name="Singhania",
        official_email="rajesh.director@gocompliances.in",
        mobile_number="+919811100099",
        date_of_joining=date(2020, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        is_reporting_manager=True,
        must_change_password=False,
    )
    # User 5: Cross-company Operations Employee at LegalCorp
    ops_user = User(
        employee_code="LC0030",
        company_id=comp_b.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_ops.designation_id,
        first_name="Vikram",
        last_name="Nair",
        official_email="vikram.ops@legalcorp.in",
        mobile_number="+919811100030",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # User 6: Salesperson with inactive company
    inactive_comp_user = User(
        employee_code="IC0001",
        company_id=comp_c_inactive.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Anita",
        last_name="Roy",
        official_email="anita@inactive.test",
        mobile_number="+919811100050",
        date_of_joining=date(2025, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add_all([
        karishma, rahul, priya, admin_director,
        ops_user, inactive_comp_user,
    ])
    db_session.flush()

    # Permissions setup:
    # Karishma: SALES (SELF), SALES_REGISTER (SELF), SALES_MY_ORDERS (SELF), SALES_CONFIRMED_ORDER (SELF), SALES_DASHBOARD (SELF)
    for mod_code in ["SALES", "SALES_REGISTER", "SALES_MY_ORDERS", "SALES_CONFIRMED_ORDER", "SALES_DASHBOARD"]:
        perm = UserModulePermission(
            user_id=karishma.user_id,
            module_id=modules[mod_code].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_approve=False,
            data_scope="SELF",
        )
        db_session.add(perm)

    # Rahul: Same as Karishma (SELF)
    for mod_code in ["SALES", "SALES_REGISTER", "SALES_MY_ORDERS", "SALES_CONFIRMED_ORDER", "SALES_DASHBOARD"]:
        perm = UserModulePermission(
            user_id=rahul.user_id,
            module_id=modules[mod_code].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_approve=False,
            data_scope="SELF",
        )
        db_session.add(perm)

    # Priya: Same (SELF)
    for mod_code in ["SALES", "SALES_REGISTER", "SALES_MY_ORDERS", "SALES_CONFIRMED_ORDER", "SALES_DASHBOARD"]:
        perm = UserModulePermission(
            user_id=priya.user_id,
            module_id=modules[mod_code].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_approve=False,
            data_scope="SELF",
        )
        db_session.add(perm)

    # Admin Director: ALL scope for SALES and OPERATIONS
    for mod_code in ["SALES", "SALES_REGISTER", "SALES_MY_ORDERS", "SALES_CONFIRMED_ORDER", "SALES_DASHBOARD", "OPERATIONS", "OPERATIONS_DASHBOARD"]:
        perm = UserModulePermission(
            user_id=admin_director.user_id,
            module_id=modules[mod_code].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            data_scope="ALL",
        )
        db_session.add(perm)

    # Inactive Comp User: SALES (SELF)
    for u in [inactive_comp_user]:
        for mod_code in ["SALES", "SALES_REGISTER"]:
            perm = UserModulePermission(
                user_id=u.user_id,
                module_id=modules[mod_code].module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=False,
                can_approve=False,
                data_scope="SELF",
            )
            db_session.add(perm)

    db_session.flush()

    return {
        "comp_a": comp_a,
        "comp_b": comp_b,
        "comp_c_inactive": comp_c_inactive,
        "service": service,
        "karishma": karishma,
        "rahul": rahul,
        "priya": priya,
        "admin_director": admin_director,
        "ops_user": ops_user,
        "inactive_comp_user": inactive_comp_user,
    }


def auth_header(user: User) -> dict:
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Requirement 1: Gocompliances salesperson creates sale without company_id -> backend assigns Gocompliances
# ============================================================================
def test_karishma_creates_sale_without_company_id_auto_assigned(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    payload = {
        "order_date": "2026-03-01",
        "client_name": "Karishma Test Client",
        "contact_no": "9812345678",
        "service_id": str(f["service"].service_id),
        "salesperson_user_id": str(f["karishma"].user_id),
        "lead_source": "WEBSITE",
        "order_value": 10000.0,
        "amount_received": 5000.0,
        "govt_fees": 1500.0,
        "incidental_cost": 500.0,
        "gst_invoice_required": False,
        "auto_confirm": True,
    }

    res = client.post("/api/sales/orders", json=payload, headers=auth_header(f["karishma"]))
    assert res.status_code == status.HTTP_201_CREATED, res.json()
    data = res.json()
    assert data["client_name"] == "Karishma Test Client"
    assert data["company_id"] == str(f["comp_a"].company_id)
    assert data["company_name"] == f["comp_a"].company_name

    # Verify directly in DB
    order = db_session.get(SalesOrder, uuid.UUID(data["order_id"]))
    assert order is not None
    assert order.company_id == f["comp_a"].company_id


# ============================================================================
# Requirement 2: Supplying another company_id is rejected
# ============================================================================
def test_karishma_supplying_different_company_id_is_rejected(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    payload = {
        "order_date": "2026-03-01",
        "company_id": str(f["comp_b"].company_id),  # Attempting to assign LegalCorp
        "client_name": "Tampered Company Client",
        "contact_no": "9812345678",
        "service_id": str(f["service"].service_id),
        "salesperson_user_id": str(f["karishma"].user_id),
        "lead_source": "WEBSITE",
        "order_value": 10000.0,
        "amount_received": 5000.0,
        "auto_confirm": True,
    }

    res = client.post("/api/sales/orders", json=payload, headers=auth_header(f["karishma"]))
    assert res.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN)
    err = res.json()["detail"]
    assert "conflicts with the provided company ID" in err or "Cannot create sales entry for another company" in err


# ============================================================================
# Requirement 3: Salesperson from another company creates sales for their own company
# ============================================================================
def test_priya_from_legalcorp_creates_sales_for_legalcorp(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    payload = {
        "order_date": "2026-03-02",
        "client_name": "Priya LegalCorp Client",
        "contact_no": "9812345679",
        "service_id": str(f["service"].service_id),
        "salesperson_user_id": str(f["priya"].user_id),
        "lead_source": "REFERRAL",
        "order_value": 15000.0,
        "amount_received": 15000.0,
        "auto_confirm": True,
    }

    res = client.post("/api/sales/orders", json=payload, headers=auth_header(f["priya"]))
    assert res.status_code == status.HTTP_201_CREATED, res.json()
    data = res.json()
    assert data["company_id"] == str(f["comp_b"].company_id)
    assert data["company_name"] == f["comp_b"].company_name

    order = db_session.get(SalesOrder, uuid.UUID(data["order_id"]))
    assert order.company_id == f["comp_b"].company_id


# ============================================================================
# Requirement 4: Ordinary salespersons cannot switch companies or access other salespersons' records
# ============================================================================
def test_ordinary_salesperson_scoping_and_isolation(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    # 1. Create order for Karishma (Comp A)
    res_k = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Karishma Private Client",
            "contact_no": "9812345601",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["karishma"].user_id),
            "lead_source": "WEBSITE",
            "order_value": 10000.0,
            "amount_received": 5000.0,
            "auto_confirm": True,
        },
        headers=auth_header(f["karishma"]),
    )
    karishma_order_id = res_k.json()["order_id"]

    # 2. Create order for Rahul (Comp A)
    res_r = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Rahul Private Client",
            "contact_no": "9812345602",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["rahul"].user_id),
            "lead_source": "DIRECT",
            "order_value": 12000.0,
            "amount_received": 6000.0,
            "auto_confirm": True,
        },
        headers=auth_header(f["rahul"]),
    )
    rahul_order_id = res_r.json()["order_id"]

    # 3. Create order for Priya (Comp B)
    res_p = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Priya Private Client",
            "contact_no": "9812345603",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["priya"].user_id),
            "lead_source": "DIRECT",
            "order_value": 8000.0,
            "amount_received": 4000.0,
            "auto_confirm": True,
        },
        headers=auth_header(f["priya"]),
    )
    priya_order_id = res_p.json()["order_id"]

    # Check Karishma's register: only sees her own order
    reg_k = client.get("/api/sales/register", headers=auth_header(f["karishma"]))
    assert reg_k.status_code == status.HTTP_200_OK
    items_k = reg_k.json()["items"]
    ids_k = [item["order_id"] for item in items_k]
    assert karishma_order_id in ids_k
    assert rahul_order_id not in ids_k
    assert priya_order_id not in ids_k

    # Supplying company_id filter for LegalCorp does NOT widen Karishma's access
    reg_k_filtered = client.get(
        f"/api/sales/register?company_id={f['comp_b'].company_id}",
        headers=auth_header(f["karishma"]),
    )
    assert reg_k_filtered.status_code == status.HTTP_200_OK
    assert len(reg_k_filtered.json()["items"]) == 0

    # Karishma cannot access Rahul's or Priya's order directly by ID
    res_direct_r = client.get(f"/api/sales/orders/{rahul_order_id}", headers=auth_header(f["karishma"]))
    assert res_direct_r.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    res_direct_p = client.get(f"/api/sales/orders/{priya_order_id}", headers=auth_header(f["karishma"]))
    assert res_direct_p.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    # Karishma can access her own order by ID
    res_direct_k = client.get(f"/api/sales/orders/{karishma_order_id}", headers=auth_header(f["karishma"]))
    assert res_direct_k.status_code == status.HTTP_200_OK


# ============================================================================
# Requirement 5: Director/Admin retain permitted all-company access
# ============================================================================
def test_director_admin_multi_company_access(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    # Admin can see all records
    reg_admin = client.get("/api/sales/register", headers=auth_header(f["admin_director"]))
    assert reg_admin.status_code == status.HTTP_200_OK

    # Admin can filter by company A
    reg_comp_a = client.get(
        f"/api/sales/register?company_id={f['comp_a'].company_id}",
        headers=auth_header(f["admin_director"]),
    )
    assert reg_comp_a.status_code == status.HTTP_200_OK

    # Admin can create sales order for Company B with Priya as salesperson
    payload = {
        "order_date": "2026-03-03",
        "company_id": str(f["comp_b"].company_id),
        "client_name": "Admin Created LegalCorp Client",
        "contact_no": "9812345688",
        "service_id": str(f["service"].service_id),
        "salesperson_user_id": str(f["priya"].user_id),
        "lead_source": "DIRECT",
        "order_value": 20000.0,
        "amount_received": 10000.0,
        "auto_confirm": True,
    }
    res = client.post("/api/sales/orders", json=payload, headers=auth_header(f["admin_director"]))
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()["company_id"] == str(f["comp_b"].company_id)


# ============================================================================
# Requirement 6: Ordinary edits cannot change record company
# ============================================================================
def test_ordinary_edits_cannot_change_record_company(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    # Karishma creates an order
    res = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Edit Test Client",
            "contact_no": "9812345699",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["karishma"].user_id),
            "lead_source": "WEBSITE",
            "order_value": 10000.0,
            "amount_received": 5000.0,
            "auto_confirm": False,
        },
        headers=auth_header(f["karishma"]),
    )
    order_id = res.json()["order_id"]

    # Karishma edits the order (trying to change client name, amount, etc.)
    res_edit = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "client_name": "Edited Client Name",
            "order_value": 15000.0,
            "amount_received": 7500.0,
        },
        headers=auth_header(f["karishma"]),
    )
    assert res_edit.status_code == status.HTTP_200_OK

    # Verify company_id remained strictly Comp A
    order = db_session.get(SalesOrder, uuid.UUID(order_id))
    assert order.company_id == f["comp_a"].company_id
    assert order.client.client_name == "Edited Client Name"
    assert order.order_value == Decimal("15000.00")


# ============================================================================
# Requirement 7: Employee company changes affect new sales only
# ============================================================================
def test_employee_company_change_affects_new_sales_only(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    # 1. Karishma creates an order while in Comp A
    res1 = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Historical Order Comp A",
            "contact_no": "9812345601",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["karishma"].user_id),
            "lead_source": "WEBSITE",
            "order_value": 10000.0,
            "amount_received": 5000.0,
            "auto_confirm": True,
        },
        headers=auth_header(f["karishma"]),
    )
    order1_id = res1.json()["order_id"]

    # 2. Transfer Karishma to Comp B in Employee Master
    karishma_user = db_session.get(User, f["karishma"].user_id)
    karishma_user.company_id = f["comp_b"].company_id
    db_session.flush()

    # 3. Karishma creates a new order after transfer
    res2 = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-05",
            "client_name": "New Order Comp B",
            "contact_no": "9812345602",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["karishma"].user_id),
            "lead_source": "WEBSITE",
            "order_value": 20000.0,
            "amount_received": 10000.0,
            "auto_confirm": True,
        },
        headers=auth_header(f["karishma"]),
    )
    assert res2.status_code == status.HTTP_201_CREATED
    order2_id = res2.json()["order_id"]

    # Verify historical order still belongs to Comp A
    order1 = db_session.get(SalesOrder, uuid.UUID(order1_id))
    assert order1.company_id == f["comp_a"].company_id

    # Verify new order belongs to Comp B
    order2 = db_session.get(SalesOrder, uuid.UUID(order2_id))
    assert order2.company_id == f["comp_b"].company_id


# ============================================================================
# Requirement 8: Missing/inactive employee company blocks creation
# ============================================================================
def test_missing_or_inactive_company_blocks_creation(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture

    # Test inactive company user
    res_inactive = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Inactive Company Client",
            "contact_no": "9812345601",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["inactive_comp_user"].user_id),
            "lead_source": "WEBSITE",
            "order_value": 10000.0,
            "amount_received": 5000.0,
            "auto_confirm": True,
        },
        headers=auth_header(f["inactive_comp_user"]),
    )
    assert res_inactive.status_code == status.HTTP_400_BAD_REQUEST
    err_inactive = res_inactive.json()["detail"]
    assert "company is missing or inactive" in err_inactive or "company is inactive or not found" in err_inactive


# ============================================================================
# Requirement 9: Cross-company Operations assignment works without changing sale company
# ============================================================================
def test_cross_company_operations_assignment_preserves_sale_company(
    client: TestClient, db_session: Session, enforcement_fixture
):
    f = enforcement_fixture
    # 1. Karishma creates an order in Comp A with auto_confirm=True
    res = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Cross Company Client",
            "contact_no": "9812345601",
            "service_id": str(f["service"].service_id),
            "salesperson_user_id": str(f["karishma"].user_id),
            "lead_source": "WEBSITE",
            "order_value": 10000.0,
            "amount_received": 5000.0,
            "auto_confirm": True,
        },
        headers=auth_header(f["karishma"]),
    )
    order_id = res.json()["order_id"]

    # 2. Operations Manager (Admin Director) assigns the order to Vikram (who is in LegalCorp / Comp B)
    res_assign = client.post(
        f"/api/sales/orders/{order_id}/assign",
        json={
            "assignee_user_id": str(f["ops_user"].user_id),
            "priority": "HIGH",
            "target_due_date": "2026-03-20",
            "notes": "Assigned cross-company to Vikram",
        },
        headers=auth_header(f["admin_director"]),
    )
    assert res_assign.status_code == status.HTTP_200_OK
    data = res_assign.json()
    assert data["assigned_to_user_id"] == str(f["ops_user"].user_id)
    assert data["company_id"] == str(f["comp_a"].company_id)

    # 3. Verify in DB that SalesOrder and OperationApplication retained Company A as origin
    order = db_session.get(SalesOrder, uuid.UUID(order_id))
    assert order.company_id == f["comp_a"].company_id

    app_record = db_session.query(OperationApplication).filter(
        OperationApplication.sales_order_id == uuid.UUID(order_id)
    ).first()
    assert app_record is not None
    assert app_record.assigned_to_user_id == f["ops_user"].user_id
    assert app_record.company_id == f["comp_a"].company_id


# ============================================================================
# Requirement 10: Super Admin creates sale on behalf of another company's salesperson
# ============================================================================
def test_super_admin_creates_sale_for_other_company_salesperson_without_explicit_company_id(
    client: TestClient, db_session: Session, enforcement_fixture
):
    """Verify:

    Super Admin (on-roll Comp A) selects Priya (on-roll Comp B).
    Originating company is automatically derived as Comp B.
    created_by is Super Admin, salesperson_user_id is Priya.
    """
    f = enforcement_fixture
    payload = {
        "order_date": "2026-03-05",
        "client_name": "SuperAdmin Cross-Company Client",
        "contact_no": "9812345699",
        "service_id": str(f["service"].service_id),
        "salesperson_user_id": str(f["priya"].user_id),  # Priya is in Comp B
        "lead_source": "WEBSITE",
        "order_value": 25000.0,
        "amount_received": 12500.0,
        "govt_fees": 1500.0,
        "incidental_cost": 500.0,
        "auto_confirm": True,
    }

    # Super Admin (Admin Director) creates sale
    res = client.post("/api/sales/orders", json=payload, headers=auth_header(f["admin_director"]))
    assert res.status_code == status.HTTP_201_CREATED, res.json()
    data = res.json()

    # The sale's company_id must be Comp B (Priya's company), NOT Comp A (Admin's company)
    assert data["company_id"] == str(f["comp_b"].company_id)
    assert data["company_name"] == f["comp_b"].company_name
    assert data["salesperson_name"] == "Priya Patel"

    # Verify directly in DB
    order = db_session.get(SalesOrder, uuid.UUID(data["order_id"]))
    assert order is not None
    assert order.company_id == f["comp_b"].company_id
    assert order.salesperson_user_id == f["priya"].user_id


def test_super_admin_conflicting_company_id_payload_is_rejected(
    client: TestClient, db_session: Session, enforcement_fixture
):
    """Verify:

    If an explicit conflicting company_id is provided (e.g. Comp A while salesperson is in Comp B),
    the backend rejects it with a clear 400 error.
    """
    f = enforcement_fixture
    payload = {
        "order_date": "2026-03-05",
        "company_id": str(f["comp_a"].company_id),  # Conflicting with Priya's Comp B
        "client_name": "Conflicting Company Client",
        "contact_no": "9812345699",
        "service_id": str(f["service"].service_id),
        "salesperson_user_id": str(f["priya"].user_id),  # Priya is in Comp B
        "lead_source": "WEBSITE",
        "order_value": 25000.0,
        "amount_received": 12500.0,
        "auto_confirm": True,
    }

    res = client.post("/api/sales/orders", json=payload, headers=auth_header(f["admin_director"]))
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    err = res.json()["detail"]
    assert "Selected salesperson belongs to company" in err or "does not belong to specified company" in err

