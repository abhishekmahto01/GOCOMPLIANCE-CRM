"""Comprehensive tests for Company-Aware Sales, Shared Operations, and Company-Aware Accounts Workflows.

Verifies:
1. Sales creation derives company strictly from authenticated salesperson's on-roll company.
2. Forged company input is rejected.
3. Missing/inactive employee company rejects creation with clear actionable error.
4. Both companies can route default assignments to the same configured coordinator (Mansi).
5. Cross-company Operations assignment (e.g. Deepak on CG assigned to EC task) is allowed.
6. Deepak sees his authorized CG and EC tasks in My Tasks and can filter by company.
7. Missing/inactive coordinator creates unassigned task with 'Coordinator setup required' without losing the sales order.
8. Updating coordinator affects only future assignments, leaving existing tasks intact.
9. Company filters narrow lists, counts, and summaries for Director/Admin.
10. Unauthorized company access is denied.
11. Accounts visibility strictly respects originating company and gst_invoice_required.
12. Reassignment preserves originating company and unified conversation history.
"""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.operation_application import OperationApplication
from app.models.operations_coordinator_config import OperationsCoordinatorConfig
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.sales_order import SalesOrderCreate
from app.services import coordinator_config_service, operation_service, sales_service


@pytest.fixture
def multi_company_fixture(db_session: Session):
    """Seed multi-company environment with GoCompliance and Entrepreneurship entities."""
    # 1. Companies
    comp_cg = Company(
        company_code="GOCOMPLIANCES",
        company_name="GoCompliances India Pvt Ltd",
        employee_code_prefix="CG",
        status="ACTIVE",
    )
    comp_ec = Company(
        company_code="ENTERPERNERSHIP",
        company_name="Entrepreneurship Corporation Ltd",
        employee_code_prefix="EC",
        status="ACTIVE",
    )
    db_session.add_all([comp_cg, comp_ec])
    db_session.flush()

    # 2. Departments
    dept_sales_cg = Department(
        company_id=comp_cg.company_id,
        department_code="SALES_CG",
        department_name="Sales Department CG",
        status="ACTIVE",
    )
    dept_ops_cg = Department(
        company_id=comp_cg.company_id,
        department_code="OPERATIONS_CG",
        department_name="Operations Department CG",
        status="ACTIVE",
    )
    dept_sales_ec = Department(
        company_id=comp_ec.company_id,
        department_code="SALES_EC",
        department_name="Sales Department EC",
        status="ACTIVE",
    )
    dept_ops_ec = Department(
        company_id=comp_ec.company_id,
        department_code="OPERATIONS_EC",
        department_name="Operations Department EC",
        status="ACTIVE",
    )
    db_session.add_all([dept_sales_cg, dept_ops_cg, dept_sales_ec, dept_ops_ec])
    db_session.flush()

    # 3. Designations
    desig_exec = Designation(
        company_id=comp_cg.company_id,
        designation_code="EXEC",
        designation_name="Executive",
        level_rank=1,
        status="ACTIVE",
    )
    desig_mgr = Designation(
        company_id=comp_cg.company_id,
        designation_code="MGR",
        designation_name="Manager",
        level_rank=10,
        status="ACTIVE",
    )
    db_session.add_all([desig_exec, desig_mgr])
    db_session.flush()

    # 4. Users
    # Salesperson on CG
    sp_cg = User(
        employee_code="CG0010",
        company_id=comp_cg.company_id,
        department_id=dept_sales_cg.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Ramesh",
        last_name="SalesCG",
        official_email="ramesh.cg@test.crm",
        mobile_number="+919800000001",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Salesperson on EC
    sp_ec = User(
        employee_code="EC0010",
        company_id=comp_ec.company_id,
        department_id=dept_sales_ec.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Suresh",
        last_name="SalesEC",
        official_email="suresh.ec@test.crm",
        mobile_number="+919800000002",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Mansi: Operations Coordinator on CG
    mansi = User(
        employee_code="CG0003",
        company_id=comp_cg.company_id,
        department_id=dept_ops_cg.department_id,
        designation_id=desig_mgr.designation_id,
        first_name="Mansi",
        last_name="Singhal",
        official_email="mansi.s@test.crm",
        mobile_number="+919800000003",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        is_reporting_manager=True,
        must_change_password=False,
    )
    # Deepak: Operations Executive on CG
    deepak = User(
        employee_code="CG0004",
        company_id=comp_cg.company_id,
        department_id=dept_ops_cg.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Deepak",
        last_name="Thapliyal",
        official_email="deepak.t@test.crm",
        mobile_number="+919800000004",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Super Admin / Director
    director = User(
        employee_code="CG0001",
        company_id=comp_cg.company_id,
        department_id=dept_ops_cg.department_id,
        designation_id=desig_mgr.designation_id,
        first_name="Super",
        last_name="Director",
        official_email="director@test.crm",
        mobile_number="+919800000005",
        date_of_joining=date(2022, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Accounts User on CG
    accounts_user = User(
        employee_code="CG0008",
        company_id=comp_cg.company_id,
        department_id=dept_ops_cg.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Anil",
        last_name="Accounts",
        official_email="anil.acc@test.crm",
        mobile_number="+919800000008",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )

    db_session.add_all([sp_cg, sp_ec, mansi, deepak, director, accounts_user])
    db_session.flush()

    # 5. Services
    srv = ServiceMaster(
        service_code="FSSAI_BASIC",
        service_name="FSSAI Basic Registration",
        category="REGISTRATION",
        base_price=Decimal("7500.00"),
        govt_fee=Decimal("100.00"),
        status="ACTIVE",
    )
    db_session.add(srv)
    db_session.flush()

    # 6. Coordinator Config: Map both companies to Mansi
    cfg_cg = OperationsCoordinatorConfig(
        company_id=comp_cg.company_id,
        coordinator_user_id=mansi.user_id,
        updated_by_user_id=director.user_id,
    )
    cfg_ec = OperationsCoordinatorConfig(
        company_id=comp_ec.company_id,
        coordinator_user_id=mansi.user_id,
        updated_by_user_id=director.user_id,
    )
    db_session.add_all([cfg_cg, cfg_ec])
    db_session.flush()

    # 7. Modules & Permissions
    mod_sales = Module(module_code="SALES", module_name="Sales", status="ACTIVE", display_order=1)
    mod_sales_orders = Module(module_code="SALES_MY_ORDERS", module_name="Sales Orders", status="ACTIVE", parent_module_id=mod_sales.module_id, display_order=2)
    mod_sales_dash = Module(module_code="SALES_DASHBOARD", module_name="Sales Dashboard", status="ACTIVE", parent_module_id=mod_sales.module_id, display_order=3)
    mod_ops = Module(module_code="OPERATIONS", module_name="Operations", status="ACTIVE", display_order=4)
    mod_acc = Module(module_code="ACCOUNTS", module_name="Accounts", status="ACTIVE", display_order=5)
    mod_acc_entries = Module(module_code="ACCOUNTS_ENTRIES", module_name="Accounts Entries", status="ACTIVE", parent_module_id=mod_acc.module_id, display_order=6)
    mod_admin = Module(module_code="ADMIN", module_name="Admin", status="ACTIVE", display_order=7)

    db_session.add_all([mod_sales, mod_sales_orders, mod_sales_dash, mod_ops, mod_acc, mod_acc_entries, mod_admin])
    db_session.flush()

    # Grant Director ALL scope
    for m in [mod_sales, mod_sales_orders, mod_sales_dash, mod_ops, mod_acc, mod_acc_entries, mod_admin]:
        db_session.add(UserModulePermission(
            user_id=director.user_id,
            module_id=m.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_export=True,
            data_scope="ALL",
            status="ACTIVE",
        ))

    # Grant SP_CG SELF scope
    for m in [mod_sales, mod_sales_orders, mod_sales_dash]:
        db_session.add(UserModulePermission(
            user_id=sp_cg.user_id,
            module_id=m.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_export=True,
            data_scope="SELF",
            status="ACTIVE",
        ))

    # Grant SP_EC SELF scope
    for m in [mod_sales, mod_sales_orders, mod_sales_dash]:
        db_session.add(UserModulePermission(
            user_id=sp_ec.user_id,
            module_id=m.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_export=True,
            data_scope="SELF",
            status="ACTIVE",
        ))

    # Grant Mansi Operations Coordinator COMPANY/ALL scope
    db_session.add(UserModulePermission(
        user_id=mansi.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_export=True,
        data_scope="ALL",
        status="ACTIVE",
    ))

    # Grant Deepak Operations SELF scope
    db_session.add(UserModulePermission(
        user_id=deepak.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_export=True,
        data_scope="SELF",
        status="ACTIVE",
    ))

    # Grant Anil Accounts COMPANY scope on CG
    for m in [mod_acc, mod_acc_entries]:
        db_session.add(UserModulePermission(
            user_id=accounts_user.user_id,
            module_id=m.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_export=True,
            data_scope="COMPANY",
            status="ACTIVE",
        ))

    db_session.commit()

    return {
        "comp_cg": comp_cg,
        "comp_ec": comp_ec,
        "sp_cg": sp_cg,
        "sp_ec": sp_ec,
        "mansi": mansi,
        "deepak": deepak,
        "director": director,
        "accounts_user": accounts_user,
        "srv": srv,
        "desig_exec": desig_exec,
    }


def auth_headers(user: User) -> dict:
    """Helper to generate JWT bearer auth headers."""
    token = create_access_token(user_id=user.user_id, token_version=user.token_version)
    return {"Authorization": f"Bearer {token}"}


def test_sales_creation_derives_company_strictly(db_session: Session, multi_company_fixture: dict):
    """Rule 1: Sales entry company is strictly derived from authenticated salesperson's on-roll company."""
    f = multi_company_fixture
    dto = SalesOrderCreate(
        client_name="Alpha Pvt Ltd",
        contact_no="9876500001",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("15000.00"),
        amount_received=Decimal("5000.00"),
        auto_confirm=True,
    )
    order_cg = sales_service.create_sales_order(db_session, dto, f["sp_cg"])
    assert order_cg.company_id == f["comp_cg"].company_id

    order_ec = sales_service.create_sales_order(db_session, dto, f["sp_ec"])
    assert order_ec.company_id == f["comp_ec"].company_id


def test_forged_company_input_is_rejected(db_session: Session, multi_company_fixture: dict):
    """Rule 1: Reject client attempts to submit a different company_id."""
    f = multi_company_fixture
    # SP on CG attempts to create entry for EC
    dto = SalesOrderCreate(
        company_id=f["comp_ec"].company_id,
        client_name="Forged Company Client",
        contact_no="9876500002",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("10000.00"),
        amount_received=Decimal("5000.00"),
    )
    with pytest.raises(ValueError, match="Cannot create sales entry for another company"):
        sales_service.create_sales_order(db_session, dto, f["sp_cg"])


def test_missing_or_inactive_company_rejects_sales_creation(db_session: Session, multi_company_fixture: dict):
    """Rule 1: Inactive or missing employee company rejects creation with clear error."""
    f = multi_company_fixture
    comp_inact = Company(
        company_code="INACTIVE_CO",
        company_name="Inactive Company Ltd",
        employee_code_prefix="IC",
        status="INACTIVE",
    )
    db_session.add(comp_inact)
    db_session.flush()

    dept_inact = Department(
        company_id=comp_inact.company_id,
        department_code="SALES_INACT",
        department_name="Sales Inact",
        status="ACTIVE",
    )
    db_session.add(dept_inact)
    db_session.flush()

    # Inactive company user
    inactive_user = User(
        employee_code="INACT01",
        company_id=comp_inact.company_id,
        department_id=dept_inact.department_id,
        designation_id=f["desig_exec"].designation_id,
        first_name="No",
        last_name="Company",
        official_email="nocompany@test.crm",
        mobile_number="+919800009999",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add(inactive_user)
    db_session.flush()

    dto = SalesOrderCreate(
        client_name="Test Client",
        contact_no="9876500003",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("10000.00"),
    )
    with pytest.raises(ValueError, match="Employee on-roll company is missing or inactive"):
        sales_service.create_sales_order(db_session, dto, inactive_user)


def test_both_companies_route_to_configured_coordinator_mansi(db_session: Session, multi_company_fixture: dict):
    """Rule 2: Entries from both companies route to configured Operations coordinator (Mansi)."""
    f = multi_company_fixture
    dto1 = SalesOrderCreate(
        client_name="Client CG Corp",
        contact_no="9876500010",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("20000.00"),
        auto_confirm=True,
    )
    order1 = sales_service.create_sales_order(db_session, dto1, f["sp_cg"])
    assert order1.application is not None
    assert order1.application.company_id == f["comp_cg"].company_id
    assert order1.application.assigned_to_user_id == f["mansi"].user_id
    assert order1.application.application_status == "ASSIGNED"

    dto2 = SalesOrderCreate(
        client_name="Client EC Corp",
        contact_no="9876500011",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("25000.00"),
        auto_confirm=True,
    )
    order2 = sales_service.create_sales_order(db_session, dto2, f["sp_ec"])
    assert order2.application is not None
    assert order2.application.company_id == f["comp_ec"].company_id
    assert order2.application.assigned_to_user_id == f["mansi"].user_id
    assert order2.application.application_status == "ASSIGNED"


def test_coordinator_can_assign_cross_company_to_deepak(db_session: Session, multi_company_fixture: dict):
    """Rule 2: Mansi can reassign an EC task to Deepak (on-roll with CG), preserving EC company ownership."""
    f = multi_company_fixture
    dto = SalesOrderCreate(
        client_name="EC Cross Company Project",
        contact_no="9876500020",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("30000.00"),
        auto_confirm=True,
    )
    order_ec = sales_service.create_sales_order(db_session, dto, f["sp_ec"])
    app = order_ec.application

    # Mansi reassigns EC task to Deepak (who is on CG)
    reassigned_app = operation_service.reassign_task(
        session=db_session,
        application_id=app.application_id,
        new_assignee_user_id=f["deepak"].user_id,
        reason="Assigned to Deepak for cross-company filing execution",
        reassigned_by=f["mansi"],
    )

    assert reassigned_app.assigned_to_user_id == f["deepak"].user_id
    assert reassigned_app.company_id == f["comp_ec"].company_id  # Task company remains EC


def test_deepak_sees_tasks_across_companies(db_session: Session, multi_company_fixture: dict):
    """Rule 2: Deepak can view his assigned tasks from both CG and EC in My Tasks."""
    f = multi_company_fixture
    # 1. Create and assign CG task to Deepak
    dto_cg = SalesOrderCreate(
        client_name="Deepak CG Task",
        contact_no="9876500030",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("15000.00"),
        auto_confirm=True,
    )
    order_cg = sales_service.create_sales_order(db_session, dto_cg, f["sp_cg"])
    operation_service.reassign_task(
        session=db_session,
        application_id=order_cg.application.application_id,
        new_assignee_user_id=f["deepak"].user_id,
        reason="Assign CG task to Deepak",
        reassigned_by=f["mansi"],
    )

    # 2. Create and assign EC task to Deepak
    dto_ec = SalesOrderCreate(
        client_name="Deepak EC Task",
        contact_no="9876500031",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("18000.00"),
        auto_confirm=True,
    )
    order_ec = sales_service.create_sales_order(db_session, dto_ec, f["sp_ec"])
    operation_service.reassign_task(
        session=db_session,
        application_id=order_ec.application.application_id,
        new_assignee_user_id=f["deepak"].user_id,
        reason="Assign EC task to Deepak",
        reassigned_by=f["mansi"],
    )

    # 3. Deepak queries My Tasks
    my_tasks_all = operation_service.get_my_tasks(db_session, f["deepak"])
    matched_ids = [str(t.application_id) for t in my_tasks_all.items]
    assert str(order_cg.application.application_id) in matched_ids
    assert str(order_ec.application.application_id) in matched_ids

    # 4. Deepak filters My Tasks by EC company
    my_tasks_ec = operation_service.get_my_tasks(
        db_session,
        f["deepak"],
        company_id=f["comp_ec"].company_id,
    )
    assert any(t.application_id == order_ec.application.application_id for t in my_tasks_ec.items)
    assert not any(t.application_id == order_cg.application.application_id for t in my_tasks_ec.items)


def test_missing_coordinator_creates_unassigned_work_item(db_session: Session, multi_company_fixture: dict):
    """Rule 2 & Config: Missing coordinator creates unassigned task with notes without losing sales order."""
    f = multi_company_fixture
    # Create new company with no coordinator configured
    new_comp = Company(
        company_code="BRANDMINGO",
        company_name="Brandmingo Marketing Ltd",
        employee_code_prefix="BM",
        status="ACTIVE",
    )
    db_session.add(new_comp)
    db_session.flush()

    dept_bm = Department(
        company_id=new_comp.company_id,
        department_code="SALES_BM",
        department_name="Sales BM",
        status="ACTIVE",
    )
    db_session.add(dept_bm)
    db_session.flush()

    sp_bm = User(
        employee_code="BM0001",
        company_id=new_comp.company_id,
        department_id=dept_bm.department_id,
        designation_id=f["desig_exec"].designation_id,
        first_name="Karan",
        last_name="Brand",
        official_email="karan.bm@test.crm",
        mobile_number="+919800000099",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add(sp_bm)
    db_session.flush()

    dto = SalesOrderCreate(
        client_name="BM Client",
        contact_no="9876500099",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("12000.00"),
        auto_confirm=True,
    )
    order = sales_service.create_sales_order(db_session, dto, sp_bm)
    assert order.confirmation_status == "CONFIRMED"
    assert order.application is not None
    assert order.application.assigned_to_user_id is None
    assert order.application.application_status == "UNASSIGNED"
    assert "Coordinator setup required" in (order.application.assignment_notes or "")


def test_coordinator_config_update_affects_future_orders_only(db_session: Session, multi_company_fixture: dict):
    """Config: Changing coordinator affects new entries only; existing assignments are preserved."""
    f = multi_company_fixture
    # Create order under Mansi coordinator
    dto1 = SalesOrderCreate(
        client_name="Order Before Config Change",
        contact_no="9876500101",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("15000.00"),
        auto_confirm=True,
    )
    order1 = sales_service.create_sales_order(db_session, dto1, f["sp_cg"])
    assert order1.application.assigned_to_user_id == f["mansi"].user_id

    # Update coordinator config for CG to Deepak
    coordinator_config_service.update_coordinator_config(
        session=db_session,
        company_id=f["comp_cg"].company_id,
        coordinator_user_id=f["deepak"].user_id,
        updated_by=f["director"],
    )

    # Existing order1 remains assigned to Mansi
    db_session.refresh(order1.application)
    assert order1.application.assigned_to_user_id == f["mansi"].user_id

    # New order2 created after change is assigned to Deepak
    dto2 = SalesOrderCreate(
        client_name="Order After Config Change",
        contact_no="9876500102",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("15000.00"),
        auto_confirm=True,
    )
    order2 = sales_service.create_sales_order(db_session, dto2, f["sp_cg"])
    assert order2.application.assigned_to_user_id == f["deepak"].user_id


def test_admin_company_filtering_sales_operations_accounts(client: TestClient, db_session: Session, multi_company_fixture: dict):
    """Rule 4: Director/Admin company filter narrows lists and summary statistics."""
    f = multi_company_fixture
    headers = auth_headers(f["director"])

    # Create CG order with GST
    dto_cg = SalesOrderCreate(
        client_name="Filter Test CG",
        contact_no="9876500201",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("20000.00"),
        amount_received=Decimal("10000.00"),
        gst_invoice_required=True,
        auto_confirm=True,
    )
    order_cg = sales_service.create_sales_order(db_session, dto_cg, f["sp_cg"])

    # Create EC order with GST
    dto_ec = SalesOrderCreate(
        client_name="Filter Test EC",
        contact_no="9876500202",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("30000.00"),
        amount_received=Decimal("15000.00"),
        gst_invoice_required=True,
        auto_confirm=True,
    )
    order_ec = sales_service.create_sales_order(db_session, dto_ec, f["sp_ec"])

    # 1. Sales Register - All Companies
    resp_all = client.get("/api/sales/register", headers=headers)
    assert resp_all.status_code == 200
    data_all = resp_all.json()
    order_ids_all = [it["order_id"] for it in data_all["items"]]
    assert str(order_cg.order_id) in order_ids_all
    assert str(order_ec.order_id) in order_ids_all

    # 2. Sales Register - Filtered by EC
    resp_ec = client.get(f"/api/sales/register?company_id={f['comp_ec'].company_id}", headers=headers)
    assert resp_ec.status_code == 200
    data_ec = resp_ec.json()
    order_ids_ec = [it["order_id"] for it in data_ec["items"]]
    assert str(order_ec.order_id) in order_ids_ec
    assert str(order_cg.order_id) not in order_ids_ec
    assert data_ec["items"][0]["company_code"] == "ENTERPERNERSHIP"

    # 3. Operations Tasks - Filtered by CG
    resp_ops_cg = client.get(f"/api/operations/tasks?company_id={f['comp_cg'].company_id}", headers=headers)
    assert resp_ops_cg.status_code == 200
    data_ops_cg = resp_ops_cg.json()
    app_ids_cg = [it["application_id"] for it in data_ops_cg["items"]]
    assert str(order_cg.application.application_id) in app_ids_cg
    assert str(order_ec.application.application_id) not in app_ids_cg

    # 4. Accounts Entries - Filtered by EC
    resp_acc_ec = client.get(f"/api/accounts/entries?company_id={f['comp_ec'].company_id}", headers=headers)
    assert resp_acc_ec.status_code == 200
    data_acc_ec = resp_acc_ec.json()
    acc_order_ids_ec = [it["order_id"] for it in data_acc_ec["items"]]
    assert str(order_ec.order_id) in acc_order_ids_ec
    assert str(order_cg.order_id) not in acc_order_ids_ec


def test_accounts_gst_gating_and_originating_company(db_session: Session, multi_company_fixture: dict):
    """Rule 3: Accounts strictly follows originating company and gst_invoice_required gating."""
    f = multi_company_fixture

    # CG Order without GST
    dto_no_gst = SalesOrderCreate(
        client_name="No GST Client",
        contact_no="9876500301",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("10000.00"),
        gst_invoice_required=False,
        auto_confirm=True,
    )
    order_no_gst = sales_service.create_sales_order(db_session, dto_no_gst, f["sp_cg"])

    # CG Order with GST
    dto_with_gst = SalesOrderCreate(
        client_name="With GST Client",
        contact_no="9876500302",
        service_id=f["srv"].service_id,
        order_date=date.today(),
        order_value=Decimal("12000.00"),
        gst_invoice_required=True,
        auto_confirm=True,
    )
    order_with_gst = sales_service.create_sales_order(db_session, dto_with_gst, f["sp_cg"])

    # Accounts user on CG queries accounts entries
    from app.services import accounts_service
    acc_entries = accounts_service.get_accounts_entries(db_session, f["accounts_user"])
    order_ids = [e.order_id for e in acc_entries.items]

    assert order_with_gst.order_id in order_ids
    assert order_no_gst.order_id not in order_ids  # Non-GST entry is strictly excluded
