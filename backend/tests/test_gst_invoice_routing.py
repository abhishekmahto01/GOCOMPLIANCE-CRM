"""Comprehensive test suite for GST Invoice Required routing flag addon in Sales and Accounts modules.
Validates:
1. Unchecked entry appears in Sales but not Accounts.
2. Checked entry appears in both.
3. Editing the checkbox updates Accounts visibility and dashboard totals.
4. Operations assignment works in both cases.
5. Unchecking preserves saved Accounts data (PI, Tax Inv, Reimbursement Note, Remarks).
6. Rechecking restores visibility without duplicate records.
7. Accounts APIs reject access/update for unchecked entries (404/400).
8. Partial Sales updates do not reset the flag.
9. Permissions and company boundaries remain enforced.
"""
import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user_module_permission import UserModulePermission
from app.models.client import ClientMaster
from app.models.service import ServiceMaster
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.services.permissions import grant_or_update_permission


def auth_header(user: User) -> dict:
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def routing_fixture(db_session: Session):
    """Fixture providing multi-role users, company, services, and clients."""
    # 1. Companies
    company_a = Company(
        company_name="GoCompliance Corp",
        legal_name="GoCompliance Corporate Services Pvt Ltd",
        company_code="GC_ROUTING_A",
        employee_code_prefix="GRA",
        status="ACTIVE",
    )
    company_b = Company(
        company_name="External Corp",
        legal_name="External Legal Services Ltd",
        company_code="GC_ROUTING_B",
        employee_code_prefix="GRB",
        status="ACTIVE",
    )
    db_session.add_all([company_a, company_b])
    db_session.flush()

    # 2. Departments
    dept_sales = Department(
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    dept_acc = Department(
        department_code="ACCOUNTS",
        department_name="Accounts Department",
        status="ACTIVE",
    )
    dept_ops = Department(
        department_code="OPERATIONS",
        department_name="Operations Department",
        status="ACTIVE",
    )
    db_session.add_all([dept_sales, dept_acc, dept_ops])
    db_session.flush()

    # 3. Designations
    desig_director = Designation(
        designation_code="DIR",
        designation_name="Director",
        level_rank=20,
        status="ACTIVE",
    )
    desig_sales = Designation(
        designation_code="SALES_EXEC",
        designation_name="Sales Executive",
        level_rank=5,
        status="ACTIVE",
    )
    desig_acc = Designation(
        designation_code="ACC_EXEC",
        designation_name="Accounts Executive",
        level_rank=5,
        status="ACTIVE",
    )
    desig_ops = Designation(
        designation_code="OPS_EXEC",
        designation_name="Operations Executive",
        level_rank=5,
        status="ACTIVE",
    )
    db_session.add_all([desig_director, desig_sales, desig_acc, desig_ops])
    db_session.flush()

    # 4. Users
    super_admin = User(
        employee_code="SA9001",
        company_id=company_a.company_id,
        department_id=dept_acc.department_id,
        designation_id=desig_director.designation_id,
        first_name="Super",
        last_name="Admin",
        official_email="sa.routing@test.com",
        mobile_number="+919999900001",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    sales_user = User(
        employee_code="SL9002",
        company_id=company_a.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Sanjay",
        last_name="Sales",
        official_email="sanjay.sales@test.com",
        mobile_number="+919999900002",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    acc_user = User(
        employee_code="AC9003",
        company_id=company_a.company_id,
        department_id=dept_acc.department_id,
        designation_id=desig_acc.designation_id,
        first_name="Anjali",
        last_name="Accounts",
        official_email="anjali.acc@test.com",
        mobile_number="+919999900003",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    ops_user = User(
        employee_code="OP9004",
        company_id=company_a.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_ops.designation_id,
        first_name="Omkar",
        last_name="Ops",
        official_email="omkar.ops@test.com",
        mobile_number="+919999900004",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    company_b_user = User(
        employee_code="CB9005",
        company_id=company_b.company_id,
        department_id=dept_acc.department_id,
        designation_id=desig_acc.designation_id,
        first_name="Bob",
        last_name="CompanyB",
        official_email="bob.b@test.com",
        mobile_number="+919999900005",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    db_session.add_all([super_admin, sales_user, acc_user, ops_user, company_b_user])
    db_session.flush()

    # Permissions
    # Ensure modules exist
    sales_root = db_session.query(Module).filter(Module.module_code == "SALES").first()
    if not sales_root:
        sales_root = Module(module_code="SALES", module_name="Sales", status="ACTIVE", display_order=10)
        db_session.add(sales_root)
        db_session.flush()

    for mcode, mname, order_idx in [
        ("SALES_DASHBOARD", "Sales Dashboard", 10),
        ("SALES_MY_ORDERS", "My Sales Orders", 20),
        ("SALES_CONFIRMED_ORDER", "Create Confirmed Order", 30),
        ("SALES_REGISTER", "Sales Register", 40),
        ("ACCOUNTS", "Accounts", 50),
        ("ACCOUNTS_DASHBOARD", "Accounts Dashboard", 51),
        ("ACCOUNTS_ENTRIES", "Accounts Entries", 52),
        ("OPERATIONS", "Operations", 60),
        ("OPERATIONS_ASSIGNED", "Assigned Operations", 61),
        ("OPERATIONS_UNASSIGNED", "Unassigned Operations", 62),
    ]:
        m = db_session.query(Module).filter(Module.module_code == mcode).first()
        if not m:
            m = Module(module_code=mcode, module_name=mname, status="ACTIVE", parent_module_id=sales_root.module_id, display_order=order_idx)
            db_session.add(m)
    db_session.flush()

    # Super admin wildcard
    mod_all = db_session.query(Module).filter(Module.module_code == "ALL").first()
    if not mod_all:
        mod_all = Module(module_code="ALL", module_name="All Modules", status="ACTIVE", display_order=1)
        db_session.add(mod_all)
        db_session.flush()

    grant_or_update_permission(
        session=db_session,
        user_id=super_admin.user_id,
        module_id=mod_all.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        can_approve=True,
        can_export=True,
        data_scope="ALL",
        granted_by_user_id=super_admin.user_id,
        is_bootstrap=True,
    )

    # Sales user permissions
    for mcode in ["SALES", "SALES_ENTRY", "SALES_REGISTER", "SALES_DASHBOARD", "SALES_CONFIRMED_ORDER", "SALES_MY_ORDERS"]:
        mod = db_session.query(Module).filter(Module.module_code == mcode).first()
        if mod:
            grant_or_update_permission(
                session=db_session,
                user_id=sales_user.user_id,
                module_id=mod.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_approve=True,
                can_export=True,
                data_scope="COMPANY",
                granted_by_user_id=super_admin.user_id,
                is_bootstrap=True,
            )

    # Accounts user permissions
    for mcode in [
        "ACCOUNTS",
        "ACCOUNTS_DASHBOARD",
        "ACCOUNTS_ENTRIES",
        "ACCOUNTS_PAYMENT_REGISTER",
        "ACCOUNTS_OUTSTANDING",
        "ACCOUNTS_INVOICES",
        "ACCOUNTS_EXPENSES",
        "ACCOUNTS_REPORTS",
    ]:
        mod = db_session.query(Module).filter(Module.module_code == mcode).first()
        if not mod:
            mod = Module(module_code=mcode, module_name=mcode.replace("_", " ").title(), status="ACTIVE", display_order=50)
            db_session.add(mod)
            db_session.flush()

        grant_or_update_permission(
            session=db_session,
            user_id=acc_user.user_id,
            module_id=mod.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            can_export=True,
            data_scope="COMPANY",
            granted_by_user_id=super_admin.user_id,
            is_bootstrap=True,
        )
        grant_or_update_permission(
            session=db_session,
            user_id=company_b_user.user_id,
            module_id=mod.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            can_export=True,
            data_scope="COMPANY",
            granted_by_user_id=super_admin.user_id,
            is_bootstrap=True,
        )

    # Operations user permissions
    for mcode in ["OPERATIONS", "OPERATIONS_ASSIGNED", "OPERATIONS_UNASSIGNED"]:
        mod = db_session.query(Module).filter(Module.module_code == mcode).first()
        if mod:
            grant_or_update_permission(
                session=db_session,
                user_id=ops_user.user_id,
                module_id=mod.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_approve=True,
                can_export=True,
                data_scope="COMPANY",
                granted_by_user_id=super_admin.user_id,
                is_bootstrap=True,
            )

    # Service & Client
    service = ServiceMaster(
        service_code="SRV_ROUTING_GST",
        service_name="GST Compliance & Advisory",
        category="COMPLIANCE",
        base_price=Decimal("60000.00"),
        govt_fee=Decimal("5000.00"),
        standard_turnaround_days=10,
        status="ACTIVE",
    )
    db_session.add(service)
    db_session.flush()

    client = ClientMaster(
        company_id=company_a.company_id,
        client_name="BlueStar Logistics Ltd",
        entity_type="LIMITED",
        contact_phone="+919876543210",
        contact_email="accounts@bluestar.in",
        status="ACTIVE",
        created_by_user_id=sales_user.user_id,
    )
    db_session.add(client)
    db_session.commit()

    return {
        "company_a": company_a,
        "company_b": company_b,
        "super_admin": super_admin,
        "sales_user": sales_user,
        "acc_user": acc_user,
        "ops_user": ops_user,
        "company_b_user": company_b_user,
        "service": service,
        "client": client,
    }


def test_unchecked_entry_in_sales_not_accounts(client: TestClient, routing_fixture: dict):
    """1. An entry created with gst_invoice_required=False appears in Sales but is strictly hidden from Accounts."""
    sales_user = routing_fixture["sales_user"]
    acc_user = routing_fixture["acc_user"]
    service = routing_fixture["service"]
    cl = routing_fixture["client"]

    payload = {
        "order_date": str(date.today()),
        "client_name": cl.client_name,
        "client_id": str(cl.client_id),
        "contact_no": cl.contact_phone,
        "location": "Bandra, Mumbai",
        "service_id": str(service.service_id),
        "salesperson_user_id": str(sales_user.user_id),
        "lead_source": "WEBSITE",
        "order_value": 75000.0,
        "amount_received": 25000.0,
        "govt_fees": 5000.0,
        "incidental_cost": 2000.0,
        "gst_invoice_required": False,
        "auto_confirm": False,
    }

    # Create Sales Order
    create_res = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
    assert create_res.status_code == 201
    created_order = create_res.json()
    order_id = created_order["order_id"]
    assert created_order["gst_invoice_required"] is False

    # 1. Appears in Sales Register
    sales_reg_res = client.get("/api/sales/register", headers=auth_header(sales_user))
    assert sales_reg_res.status_code == 200
    sales_orders = sales_reg_res.json()["items"]
    matched_sales = [o for o in sales_orders if o["order_id"] == order_id]
    assert len(matched_sales) == 1
    assert matched_sales[0]["gst_invoice_required"] is False

    # 2. Does NOT appear in Accounts Entries
    acc_res = client.get("/api/accounts/entries", headers=auth_header(acc_user))
    assert acc_res.status_code == 200
    acc_entries = acc_res.json()["items"]
    matched_acc = [o for o in acc_entries if o["order_id"] == order_id]
    assert len(matched_acc) == 0

    # 3. Accounts Single Entry endpoint rejects access (404)
    acc_detail_res = client.get(f"/api/accounts/entries/{order_id}", headers=auth_header(acc_user))
    assert acc_detail_res.status_code == 404

    # 4. Accounts Update endpoint rejects update (400)
    acc_update_res = client.patch(
        f"/api/accounts/entries/{order_id}",
        json={"proforma_invoice_no": "PI-FAIL-001"},
        headers=auth_header(acc_user),
    )
    assert acc_update_res.status_code == 400


def test_checked_entry_appears_in_both_and_allows_accounts_editing(client: TestClient, routing_fixture: dict):
    """2. An entry created with gst_invoice_required=True appears in both Sales and Accounts,
    and Accounts users may update columns 15, 16, 17, 21.
    """
    sales_user = routing_fixture["sales_user"]
    acc_user = routing_fixture["acc_user"]
    service = routing_fixture["service"]
    cl = routing_fixture["client"]

    payload = {
        "order_date": str(date.today()),
        "client_name": cl.client_name,
        "client_id": str(cl.client_id),
        "contact_no": cl.contact_phone,
        "service_id": str(service.service_id),
        "salesperson_user_id": str(sales_user.user_id),
        "lead_source": "DIRECT",
        "order_value": 90000.0,
        "amount_received": 30000.0,
        "govt_fees": 6000.0,
        "incidental_cost": 1000.0,
        "gst_invoice_required": True,
        "auto_confirm": True,
    }

    create_res = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
    assert create_res.status_code == 201
    order_id = create_res.json()["order_id"]

    # 1. Appears in Sales Register
    sales_res = client.get("/api/sales/register", headers=auth_header(sales_user))
    assert sales_res.status_code == 200
    matched_sales = [o for o in sales_res.json()["items"] if o["order_id"] == order_id]
    assert len(matched_sales) == 1
    assert matched_sales[0]["gst_invoice_required"] is True

    # 2. Appears in Accounts Entries
    acc_res = client.get("/api/accounts/entries", headers=auth_header(acc_user))
    assert acc_res.status_code == 200
    matched_acc = [o for o in acc_res.json()["items"] if o["order_id"] == order_id]
    assert len(matched_acc) == 1
    assert matched_acc[0]["gst_invoice_required"] is True

    # 3. Accounts single entry detail works
    detail_res = client.get(f"/api/accounts/entries/{order_id}", headers=auth_header(acc_user))
    assert detail_res.status_code == 200
    assert detail_res.json()["order_id"] == order_id

    # 4. Accounts update allowed fields
    patch_res = client.patch(
        f"/api/accounts/entries/{order_id}",
        json={
            "proforma_invoice_no": "PI-2026-8888",
            "tax_invoice_no": "TAX-2026-8888",
            "reimbursement_note": "Filing expenses approved",
            "remarks": "Invoiced and sent to client",
        },
        headers=auth_header(acc_user),
    )
    assert patch_res.status_code == 200
    updated_acc = patch_res.json()
    assert updated_acc["proforma_invoice_no"] == "PI-2026-8888"
    assert updated_acc["tax_invoice_no"] == "TAX-2026-8888"
    assert updated_acc["reimbursement_note"] == "Filing expenses approved"
    assert updated_acc["remarks"] == "Invoiced and sent to client"


def test_toggling_checkbox_updates_accounts_and_preserves_accounts_fields(client: TestClient, routing_fixture: dict):
    """3. Verify checkbox toggling lifecycle:
    - Unchecked -> Checked: appears in Accounts and dashboard totals increase.
    - Accounts fields edited and saved.
    - Checked -> Unchecked: disappears from Accounts and dashboard totals decrease.
    - DB data (PI, Tax Inv, reimbursement note, remarks) is NOT deleted.
    - Unchecked -> Checked again: reappears in Accounts with all previously saved Accounts data intact.
    - Exact same database record (no duplicate row).
    """
    sales_user = routing_fixture["sales_user"]
    acc_user = routing_fixture["acc_user"]
    service = routing_fixture["service"]
    cl = routing_fixture["client"]

    # Step 1: Create Unchecked
    payload = {
        "order_date": str(date.today()),
        "client_name": cl.client_name,
        "client_id": str(cl.client_id),
        "contact_no": cl.contact_phone,
        "service_id": str(service.service_id),
        "salesperson_user_id": str(sales_user.user_id),
        "lead_source": "DIRECT",
        "order_value": 50000.0,
        "amount_received": 10000.0,
        "govt_fees": 5000.0,
        "incidental_cost": 0.0,
        "gst_invoice_required": False,
    }
    create_res = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
    assert create_res.status_code == 201
    order_id = create_res.json()["order_id"]

    # Accounts Dashboard before check
    dash_before_res = client.get("/api/accounts/dashboard", headers=auth_header(acc_user))
    assert dash_before_res.status_code == 200, f"Dashboard error: {dash_before_res.text}"
    dash_before = dash_before_res.json()
    count_before = dash_before["kpis"]["total_entries"]
    amount_before = dash_before["kpis"]["total_amount"]

    # Step 2: Check the box in Sales
    sales_update_1 = client.patch(
        f"/api/sales/orders/{order_id}",
        json={"gst_invoice_required": True},
        headers=auth_header(sales_user),
    )
    assert sales_update_1.status_code == 200
    assert sales_update_1.json()["gst_invoice_required"] is True

    # Check Accounts Dashboard totals increased
    dash_after_check = client.get("/api/accounts/dashboard", headers=auth_header(acc_user)).json()
    assert dash_after_check["kpis"]["total_entries"] == count_before + 1
    assert dash_after_check["kpis"]["total_amount"] == amount_before + 50000.0

    # Step 3: Accounts fills invoice and remarks
    acc_patch = client.patch(
        f"/api/accounts/entries/{order_id}",
        json={
            "proforma_invoice_no": "PI-SAVED-001",
            "tax_invoice_no": "TAX-SAVED-001",
            "reimbursement_note": "Reimbursement note preserved test",
            "remarks": "Accounts remarks preserved test",
        },
        headers=auth_header(acc_user),
    )
    assert acc_patch.status_code == 200

    # Step 4: Uncheck the box in Sales
    sales_update_2 = client.patch(
        f"/api/sales/orders/{order_id}",
        json={"gst_invoice_required": False},
        headers=auth_header(sales_user),
    )
    assert sales_update_2.status_code == 200
    assert sales_update_2.json()["gst_invoice_required"] is False

    # Disappears from Accounts Dashboard
    dash_after_uncheck = client.get("/api/accounts/dashboard", headers=auth_header(acc_user)).json()
    assert dash_after_uncheck["kpis"]["total_entries"] == count_before
    assert dash_after_uncheck["kpis"]["total_amount"] == amount_before

    # Disappears from Accounts Entries list
    acc_list_res = client.get("/api/accounts/entries", headers=auth_header(acc_user)).json()
    assert not any(item["order_id"] == order_id for item in acc_list_res["items"])

    # Accounts APIs reject access/update
    assert client.get(f"/api/accounts/entries/{order_id}", headers=auth_header(acc_user)).status_code == 404
    assert client.patch(f"/api/accounts/entries/{order_id}", json={"remarks": "test"}, headers=auth_header(acc_user)).status_code == 400

    # Step 5: Verify preserved values in Sales view
    sales_detail = client.get(f"/api/sales/orders/{order_id}", headers=auth_header(sales_user)).json()
    assert sales_detail["proforma_invoice_no"] == "PI-SAVED-001"
    assert sales_detail["tax_invoice_no"] == "TAX-SAVED-001"
    assert sales_detail["reimbursement_note"] == "Reimbursement note preserved test"

    # Step 6: Recheck the box in Sales
    sales_update_3 = client.patch(
        f"/api/sales/orders/{order_id}",
        json={"gst_invoice_required": True},
        headers=auth_header(sales_user),
    )
    assert sales_update_3.status_code == 200

    # Reappears in Accounts with all saved fields intact!
    acc_reappeared = client.get(f"/api/accounts/entries/{order_id}", headers=auth_header(acc_user)).json()
    assert acc_reappeared["order_id"] == order_id
    assert acc_reappeared["proforma_invoice_no"] == "PI-SAVED-001"
    assert acc_reappeared["tax_invoice_no"] == "TAX-SAVED-001"
    assert acc_reappeared["reimbursement_note"] == "Reimbursement note preserved test"
    assert acc_reappeared["remarks"] == "Accounts remarks preserved test"


def test_partial_sales_updates_do_not_reset_gst_invoice_required(client: TestClient, routing_fixture: dict):
    """4. Verify partial updates that omit gst_invoice_required preserve its saved value."""
    sales_user = routing_fixture["sales_user"]
    service = routing_fixture["service"]
    cl = routing_fixture["client"]

    # Create with gst_invoice_required = True
    payload = {
        "order_date": str(date.today()),
        "client_name": cl.client_name,
        "client_id": str(cl.client_id),
        "contact_no": cl.contact_phone,
        "location": "Connaught Place, Delhi",
        "service_id": str(service.service_id),
        "salesperson_user_id": str(sales_user.user_id),
        "lead_source": "WEBSITE",
        "order_value": 40000.0,
        "amount_received": 10000.0,
        "govt_fees": 2000.0,
        "incidental_cost": 1000.0,
        "gst_invoice_required": True,
    }
    create_res = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
    assert create_res.status_code == 201
    order_id = create_res.json()["order_id"]

    # Partial update: update only location and amount_received (omitting gst_invoice_required)
    patch_res = client.patch(
        f"/api/sales/orders/{order_id}",
        json={
            "location": "Saket, Delhi",
            "amount_received": 20000.0,
        },
        headers=auth_header(sales_user),
    )
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["location"] == "Saket, Delhi"
    assert float(updated_data["amount_received"]) == 20000.0
    # Must preserve True!
    assert updated_data["gst_invoice_required"] is True


def test_operations_assignment_works_for_both_checked_and_unchecked(client: TestClient, routing_fixture: dict):
    """5. Operations assignment works regardless of gst_invoice_required routing flag."""
    super_admin = routing_fixture["super_admin"]
    sales_user = routing_fixture["sales_user"]
    ops_user = routing_fixture["ops_user"]
    service = routing_fixture["service"]
    cl = routing_fixture["client"]

    # 1. Assign unchecked order
    create_unchecked = client.post(
        "/api/sales/orders",
        json={
            "order_date": str(date.today()),
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": cl.contact_phone,
            "service_id": str(service.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "lead_source": "WEBSITE",
            "order_value": 30000.0,
            "amount_received": 5000.0,
            "gst_invoice_required": False,
            "auto_confirm": True,
        },
        headers=auth_header(sales_user),
    ).json()

    assign_res1 = client.post(
        f"/api/sales/orders/{create_unchecked['order_id']}/assign",
        json={
            "assignee_user_id": str(ops_user.user_id),
            "target_due_date": str(date.today() + timedelta(days=7)),
        },
        headers=auth_header(super_admin),
    )
    assert assign_res1.status_code == 200
    assert assign_res1.json()["assigned_to_user_id"] == str(ops_user.user_id)

    # 2. Assign checked order
    create_checked = client.post(
        "/api/sales/orders",
        json={
            "order_date": str(date.today()),
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": cl.contact_phone,
            "service_id": str(service.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "lead_source": "DIRECT",
            "order_value": 35000.0,
            "amount_received": 10000.0,
            "gst_invoice_required": True,
            "auto_confirm": True,
        },
        headers=auth_header(sales_user),
    ).json()

    assign_res2 = client.post(
        f"/api/sales/orders/{create_checked['order_id']}/assign",
        json={
            "assignee_user_id": str(ops_user.user_id),
            "target_due_date": str(date.today() + timedelta(days=7)),
        },
        headers=auth_header(super_admin),
    )
    assert assign_res2.status_code == 200
    assert assign_res2.json()["assigned_to_user_id"] == str(ops_user.user_id)


def test_company_boundary_isolation_enforced(client: TestClient, routing_fixture: dict):
    """6. Company B user cannot view or edit Company A Accounts entries even if gst_invoice_required is True."""
    sales_user = routing_fixture["sales_user"]
    company_b_user = routing_fixture["company_b_user"]
    service = routing_fixture["service"]
    cl = routing_fixture["client"]

    # Create in Company A with gst_invoice_required = True
    create_res = client.post(
        "/api/sales/orders",
        json={
            "order_date": str(date.today()),
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": cl.contact_phone,
            "service_id": str(service.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "lead_source": "DIRECT",
            "order_value": 50000.0,
            "amount_received": 15000.0,
            "gst_invoice_required": True,
        },
        headers=auth_header(sales_user),
    ).json()
    order_id = create_res["order_id"]

    # Company B Accounts user accesses Company A order -> 403 / 404
    b_detail_res = client.get(f"/api/accounts/entries/{order_id}", headers=auth_header(company_b_user))
    assert b_detail_res.status_code in [403, 404]

    b_update_res = client.patch(
        f"/api/accounts/entries/{order_id}",
        json={"remarks": "Hacked from Company B"},
        headers=auth_header(company_b_user),
    )
    assert b_update_res.status_code in [400, 403, 404]
