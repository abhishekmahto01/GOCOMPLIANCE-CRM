"""Unit and integration tests for Sales Dashboard API endpoints and RBAC scoping."""
import uuid
from datetime import date, timedelta
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
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.services.permissions import grant_or_update_permission
from app.services.sales_service import create_sales_order


@pytest.fixture
def sales_dashboard_fixture(db_session: Session):
    """Seed comprehensive test organization, hierarchy, and sample orders for dashboard tests."""
    company = Company(
        company_code="GOCOMP",
        company_name="GoCompliances Technologies",
        employee_code_prefix="GC",
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    dept = Department(
        company_id=company.company_id,
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    db_session.add(dept)
    db_session.flush()

    desig_mgr = Designation(
        company_id=company.company_id,
        designation_code="SALES_HEAD",
        designation_name="Sales Head",
        level_rank=10,
        status="ACTIVE",
    )
    desig_rep = Designation(
        company_id=company.company_id,
        designation_code="SALES_EXEC",
        designation_name="Sales Executive",
        level_rank=5,
        status="ACTIVE",
    )
    db_session.add_all([desig_mgr, desig_rep])
    db_session.flush()

    # Manager User
    manager = User(
        employee_code="GC0001",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_mgr.designation_id,
        first_name="Karishma",
        last_name="Upadhyay",
        official_email="karishma@gocompliances.com",
        mobile_number="+919999900001",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        is_reporting_manager=True,
        must_change_password=False,
    )
    db_session.add(manager)
    db_session.flush()

    # Sales Rep 1 (Reports to Karishma)
    rep1 = User(
        employee_code="GC0002",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_rep.designation_id,
        manager_user_id=manager.user_id,
        first_name="Amit",
        last_name="Sharma",
        official_email="amit.s@gocompliances.com",
        mobile_number="+919999900002",
        date_of_joining=date(2023, 6, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Sales Rep 2 (Reports to Karishma)
    rep2 = User(
        employee_code="GC0003",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_rep.designation_id,
        manager_user_id=manager.user_id,
        first_name="Neha",
        last_name="Verma",
        official_email="neha.v@gocompliances.com",
        mobile_number="+919999900003",
        date_of_joining=date(2023, 6, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Other Independent Sales Rep (No manager relation)
    other_rep = User(
        employee_code="GC0004",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_rep.designation_id,
        first_name="Rohit",
        last_name="Mehta",
        official_email="rohit.m@gocompliances.com",
        mobile_number="+919999900004",
        date_of_joining=date(2023, 6, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add_all([rep1, rep2, other_rep])
    db_session.flush()

    # Modules
    sales_root = Module(
        module_code="SALES",
        module_name="Sales",
        status="ACTIVE",
        display_order=10,
    )
    sales_dash_mod = Module(
        module_code="SALES_DASHBOARD",
        module_name="Sales Dashboard",
        parent_module_id=sales_root.module_id,
        route="/sales/dashboard",
        status="ACTIVE",
        display_order=10,
    )
    sales_orders_mod = Module(
        module_code="SALES_MY_ORDERS",
        module_name="My Sales Orders",
        parent_module_id=sales_root.module_id,
        route="/sales/my-orders",
        status="ACTIVE",
        display_order=20,
    )
    db_session.add_all([sales_root, sales_dash_mod, sales_orders_mod])
    db_session.flush()

    # Permissions:
    # Manager has TEAM scope on SALES_DASHBOARD
    grant_or_update_permission(
        db_session,
        user_id=manager.user_id,
        module_id=sales_dash_mod.module_id,
        can_view=True,
        can_export=True,
        data_scope="TEAM",
        is_bootstrap=True,
    )
    # Rep1 has SELF scope on SALES_DASHBOARD
    grant_or_update_permission(
        db_session,
        user_id=rep1.user_id,
        module_id=sales_dash_mod.module_id,
        can_view=True,
        can_export=True,
        data_scope="SELF",
        is_bootstrap=True,
    )

    # Services
    srv_pvt = ServiceMaster(
        service_code="PVT_LTD",
        service_name="Private Limited",
        category="INCORPORATION",
        base_price=Decimal("15000.00"),
        status="ACTIVE",
    )
    srv_llp = ServiceMaster(
        service_code="LLP",
        service_name="LLP",
        category="INCORPORATION",
        base_price=Decimal("10000.00"),
        status="ACTIVE",
    )
    db_session.add_all([srv_pvt, srv_llp])
    db_session.flush()

    # Clients
    client1 = ClientMaster(
        company_id=company.company_id,
        client_name="Sharma Enterprises",
        entity_type="Private Limited",
        contact_person="Raj Sharma",
        contact_email="raj@sharmaenterprises.com",
        contact_phone="+919811122233",
        created_by_user_id=rep1.user_id,
        status="ACTIVE",
    )
    client2 = ClientMaster(
        company_id=company.company_id,
        client_name="Gupta Traders",
        entity_type="LLP",
        contact_person="Vikas Gupta",
        contact_email="vikas@guptatraders.com",
        contact_phone="+919811122244",
        created_by_user_id=rep2.user_id,
        status="ACTIVE",
    )
    client3 = ClientMaster(
        company_id=company.company_id,
        client_name="Other Client Ltd",
        entity_type="Private Limited",
        contact_person="Other Person",
        contact_email="other@client.com",
        contact_phone="+919811122255",
        created_by_user_id=other_rep.user_id,
        status="ACTIVE",
    )
    db_session.add_all([client1, client2, client3])
    db_session.flush()

    # Create Orders in Current Month (e.g. today)
    today = date.today()

    order1 = SalesOrder(
        order_number=f"SO-{today.year}-0001",
        company_id=company.company_id,
        client_id=client1.client_id,
        service_id=srv_pvt.service_id,
        salesperson_user_id=rep1.user_id,
        lead_source="WEBSITE",
        order_date=today,
        order_value=Decimal("100000.00"),
        amount_received=Decimal("80000.00"),
        balance_amount=Decimal("20000.00"),
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
    )
    order2 = SalesOrder(
        order_number=f"SO-{today.year}-0002",
        company_id=company.company_id,
        client_id=client2.client_id,
        service_id=srv_llp.service_id,
        salesperson_user_id=rep2.user_id,
        lead_source="REFERRAL",
        order_date=today,
        order_value=Decimal("50000.00"),
        amount_received=Decimal("50000.00"),
        balance_amount=Decimal("0.00"),
        payment_status="FULLY_PAID",
        confirmation_status="CONFIRMED",
    )
    order_other = SalesOrder(
        order_number=f"SO-{today.year}-0003",
        company_id=company.company_id,
        client_id=client3.client_id,
        service_id=srv_pvt.service_id,
        salesperson_user_id=other_rep.user_id,
        lead_source="DIRECT",
        order_date=today,
        order_value=Decimal("75000.00"),
        amount_received=Decimal("25000.00"),
        balance_amount=Decimal("50000.00"),
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
    )
    db_session.add_all([order1, order2, order_other])
    db_session.flush()

    return {
        "company": company,
        "manager": manager,
        "rep1": rep1,
        "rep2": rep2,
        "other_rep": other_rep,
        "srv_pvt": srv_pvt,
        "srv_llp": srv_llp,
        "order1": order1,
        "order2": order2,
        "order_other": order_other,
    }


def auth_header_for_user(user: User) -> dict:
    """Helper to generate Authorization header for a user."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


def test_sales_employee_self_only_visibility(client: TestClient, sales_dashboard_fixture):
    """Verify sales rep with SELF scope sees ONLY their own orders and totals."""
    f = sales_dashboard_fixture
    headers = auth_header_for_user(f["rep1"])

    resp = client.get("/api/sales/dashboard?preset=this_month", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    # Rep1 only has order1 (100,000 INR)
    assert data["kpis"]["total_sales"]["value"] == 100000.0
    assert data["kpis"]["confirmed_orders"]["value"] == 1.0
    assert data["kpis"]["amount_received"]["value"] == 80000.0
    assert data["kpis"]["outstanding"]["value"] == 20000.0
    assert data["kpis"]["total_clients"]["value"] == 1.0

    # Filter options should indicate cannot filter employees
    assert data["filter_options"]["can_filter_employees"] is False

    # Team performance table should contain ONLY rep1
    assert len(data["team_performance"]) == 1
    assert data["team_performance"][0]["salesperson_name"] == "Amit Sharma"

    # Recent orders should contain ONLY order1
    assert len(data["recent_orders"]) == 1
    assert data["recent_orders"][0]["order_number"] == f["order1"].order_number


def test_sales_employee_cannot_query_other_employee(client: TestClient, sales_dashboard_fixture):
    """Verify sales rep cannot view another rep's data by passing employee_id parameter."""
    f = sales_dashboard_fixture
    headers = auth_header_for_user(f["rep1"])

    # Attempt to query rep2's ID
    resp = client.get(
        f"/api/sales/dashboard?preset=this_month&employee_id={f['rep2'].user_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()

    # Backend strictly clamps to rep1 (self)
    assert data["kpis"]["total_sales"]["value"] == 100000.0
    assert data["team_performance"][0]["salesperson_name"] == "Amit Sharma"


def test_sales_manager_team_scope(client: TestClient, sales_dashboard_fixture):
    """Verify sales manager sees all reporting team members but NOT independent rep."""
    f = sales_dashboard_fixture
    headers = auth_header_for_user(f["manager"])

    resp = client.get("/api/sales/dashboard?preset=this_month", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    # Manager sees order1 (100k) + order2 (50k) = 150k (Excludes other_rep 75k)
    assert data["kpis"]["total_sales"]["value"] == 150000.0
    assert data["kpis"]["confirmed_orders"]["value"] == 2.0
    assert data["kpis"]["amount_received"]["value"] == 130000.0
    assert data["kpis"]["outstanding"]["value"] == 20000.0
    assert data["kpis"]["total_clients"]["value"] == 2.0

    # Team performance should have 2 rows (Amit Sharma and Neha Verma)
    assert len(data["team_performance"]) == 2
    names = {r["salesperson_name"] for r in data["team_performance"]}
    assert names == {"Amit Sharma", "Neha Verma"}

    # Manager can filter by specific team member
    resp_sub = client.get(
        f"/api/sales/dashboard?preset=this_month&employee_id={f['rep2'].user_id}",
        headers=headers,
    )
    assert resp_sub.status_code == 200
    data_sub = resp_sub.json()
    assert data_sub["kpis"]["total_sales"]["value"] == 50000.0
    assert len(data_sub["team_performance"]) == 1
    assert data_sub["team_performance"][0]["salesperson_name"] == "Neha Verma"


def test_sales_manager_disallowed_subordinate_scope(client: TestClient, sales_dashboard_fixture):
    """Verify sales manager querying an employee outside their reporting tree returns zero/empty results."""
    f = sales_dashboard_fixture
    headers = auth_header_for_user(f["manager"])

    # Query other_rep who does NOT report to manager
    resp = client.get(
        f"/api/sales/dashboard?preset=this_month&employee_id={f['other_rep'].user_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["kpis"]["total_sales"]["value"] == 0.0
    assert len(data["team_performance"]) == 0
    assert len(data["recent_orders"]) == 0


def test_sales_dashboard_export_csv(client: TestClient, sales_dashboard_fixture):
    """Verify CSV export endpoint returns formatted CSV matching permissions."""
    f = sales_dashboard_fixture
    headers = auth_header_for_user(f["rep1"])

    resp = client.get("/api/sales/dashboard/export?preset=this_month", headers=headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["Content-Type"]
    assert "sales_report_" in resp.headers["Content-Disposition"]

    content = resp.text
    assert "Order ID,Date,Client,Service,Salesperson" in content
    assert f["order1"].order_number in content
    assert f["order2"].order_number not in content  # Rep1 cannot export Rep2's order


def test_sales_dashboard_empty_db_safety(client: TestClient, db_session: Session):
    """Verify empty database returns clean zero KPIs and structures without divide-by-zero errors."""
    company = Company(
        company_code="EMPTYCO",
        company_name="Empty Company",
        employee_code_prefix="EC",
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    dept = Department(
        company_id=company.company_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    desig = Designation(
        company_id=company.company_id,
        designation_code="DIR",
        designation_name="Director",
        level_rank=10,
        status="ACTIVE",
    )
    db_session.add_all([dept, desig])
    db_session.flush()

    user = User(
        employee_code="EC0001",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig.designation_id,
        first_name="Solo",
        last_name="User",
        official_email="solo@empty.com",
        mobile_number="+919999900099",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add(user)
    db_session.flush()

    dash_mod = Module(
        module_code="SALES_DASHBOARD",
        module_name="Sales Dashboard",
        route="/sales/dashboard",
        status="ACTIVE",
    )
    db_session.add(dash_mod)
    db_session.flush()

    grant_or_update_permission(
        db_session,
        user_id=user.user_id,
        module_id=dash_mod.module_id,
        can_view=True,
        can_export=True,
        data_scope="SELF",
        is_bootstrap=True,
    )

    headers = auth_header_for_user(user)
    resp = client.get("/api/sales/dashboard?preset=this_month", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["kpis"]["total_sales"]["value"] == 0.0
    assert data["kpis"]["avg_order_value"]["value"] == 0.0
    assert data["kpis"]["confirmed_orders"]["value"] == 0.0
    assert len(data["sales_trend"]) > 0
    assert len(data["recent_orders"]) == 0
    assert len(data["team_performance"]) == 0
    assert data["payment_status"]["total_orders"] == 0
    assert data["lead_sources"]["total_leads"] == 0
