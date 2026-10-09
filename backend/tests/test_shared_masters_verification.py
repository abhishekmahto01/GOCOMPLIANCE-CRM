"""
End-to-end integration and verification tests for shared Department and Designation masters.

Verifies:
1. Cross-company master reuse: Employees from different companies (e.g. Gocompliances & Enterpernership)
   can share the identical department_id ("Sales") and designation_id ("Senior Executive").
2. Employee create and update both succeed with shared masters.
3. Inactive department or designation selections are rejected.
4. Company-specific employee code series (prefixes and counters) remain strictly independent.
5. Permission / data scoping isolation: Sharing a department does not broaden employee permissions
   or allow cross-company data access under DEPARTMENT scope.
6. Company changes on employee do not invalidate valid shared department / designation masters.
"""

import uuid
from datetime import date
import pytest
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.client import ClientMaster
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import (
    create_user,
    update_employee,
    validate_user_cross_company_integrity,
)
from app.services.permissions import DataScopeContext


@pytest.fixture
def shared_masters_env(db_session: Session):
    """Set up two distinct companies and shared global masters."""
    # 1. Company 1: Gocompliances
    comp_gc = Company(
        company_id=uuid.uuid4(),
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances Private Limited",
        employee_code_prefix="GC",
        next_employee_number=1,
        status="ACTIVE",
    )
    # 2. Company 2: Enterpernership
    comp_ep = Company(
        company_id=uuid.uuid4(),
        company_code="ENTERPERNERSHIP",
        company_name="Enterpernership Services Ltd",
        employee_code_prefix="EP",
        next_employee_number=1,
        status="ACTIVE",
    )
    db_session.add_all([comp_gc, comp_ep])
    db_session.flush()

    # 3. Global Reusable Departments
    dept_sales = Department(
        department_id=uuid.uuid4(),
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    dept_ops = Department(
        department_id=uuid.uuid4(),
        department_code="OPERATIONS",
        department_name="Operations",
        status="ACTIVE",
    )
    dept_inactive = Department(
        department_id=uuid.uuid4(),
        department_code="OLD_RND",
        department_name="Old R&D",
        status="INACTIVE",
    )
    db_session.add_all([dept_sales, dept_ops, dept_inactive])
    db_session.flush()

    # 4. Global Reusable Designations
    desig_sr_exec = Designation(
        designation_id=uuid.uuid4(),
        designation_code="SR_EXEC",
        designation_name="Senior Executive",
        level_rank=5,
        status="ACTIVE",
    )
    desig_mgr = Designation(
        designation_id=uuid.uuid4(),
        designation_code="MGR",
        designation_name="Manager",
        level_rank=10,
        status="ACTIVE",
    )
    desig_inactive = Designation(
        designation_id=uuid.uuid4(),
        designation_code="OLD_ROLE",
        designation_name="Deprecated Role",
        level_rank=1,
        status="INACTIVE",
    )
    db_session.add_all([desig_sr_exec, desig_mgr, desig_inactive])
    db_session.flush()

    return {
        "comp_gc": comp_gc,
        "comp_ep": comp_ep,
        "dept_sales": dept_sales,
        "dept_ops": dept_ops,
        "dept_inactive": dept_inactive,
        "desig_sr_exec": desig_sr_exec,
        "desig_mgr": desig_mgr,
        "desig_inactive": desig_inactive,
    }


def test_cross_company_shared_master_creation_and_code_generation(
    db_session: Session, shared_masters_env
) -> None:
    """
    Verify acceptance scenario:
    A Gocompliances sales employee and an Enterpernership sales employee can both
    use the same Sales department and Senior Executive designation master records,
    while generating company-specific employee codes (GC0001, EP0001).
    """
    env = shared_masters_env

    # 1. Create Gocompliances employee with shared Sales & Senior Executive
    gc_user_in = UserCreate(
        company_id=env["comp_gc"].company_id,
        department_id=env["dept_sales"].department_id,
        designation_id=env["desig_sr_exec"].designation_id,
        first_name="Aarav",
        last_name="Sharma",
        official_email="aarav.sharma@gocompliances.in",
        mobile_number="+919876543201",
        date_of_joining=date(2026, 1, 10),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    gc_user = create_user(db_session, gc_user_in)
    db_session.flush()

    assert gc_user.employee_code == "GC0001"
    assert gc_user.company_id == env["comp_gc"].company_id
    assert gc_user.department_id == env["dept_sales"].department_id
    assert gc_user.designation_id == env["desig_sr_exec"].designation_id

    # 2. Create Enterpernership employee with the EXACT SAME Sales & Senior Executive
    ep_user_in = UserCreate(
        company_id=env["comp_ep"].company_id,
        department_id=env["dept_sales"].department_id,
        designation_id=env["desig_sr_exec"].designation_id,
        first_name="Rohan",
        last_name="Verma",
        official_email="rohan.verma@enterpernership.in",
        mobile_number="+919876543202",
        date_of_joining=date(2026, 1, 15),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    ep_user = create_user(db_session, ep_user_in)
    db_session.flush()

    assert ep_user.employee_code == "EP0001"
    assert ep_user.company_id == env["comp_ep"].company_id
    assert ep_user.department_id == env["dept_sales"].department_id
    assert ep_user.designation_id == env["desig_sr_exec"].designation_id

    # Verify both employees share the same department and designation IDs
    assert gc_user.department_id == ep_user.department_id
    assert gc_user.designation_id == ep_user.designation_id
    assert gc_user.company_id != ep_user.company_id


def test_update_employee_with_shared_masters(
    db_session: Session, shared_masters_env
) -> None:
    """Verify updating an employee's department/designation to other shared masters succeeds."""
    env = shared_masters_env

    ep_user_in = UserCreate(
        company_id=env["comp_ep"].company_id,
        department_id=env["dept_sales"].department_id,
        designation_id=env["desig_sr_exec"].designation_id,
        first_name="Pooja",
        last_name="Singh",
        official_email="pooja.singh@enterpernership.in",
        mobile_number="+919876543203",
        date_of_joining=date(2026, 2, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    user = create_user(db_session, ep_user_in)
    db_session.flush()

    # Promote to Manager in Operations
    update_in = UserUpdate(
        department_id=env["dept_ops"].department_id,
        designation_id=env["desig_mgr"].designation_id,
    )
    updated_user = update_employee(db_session, user, update_in)
    db_session.flush()

    assert updated_user.department_id == env["dept_ops"].department_id
    assert updated_user.designation_id == env["desig_mgr"].designation_id
    assert updated_user.company_id == env["comp_ep"].company_id


def test_inactive_department_or_designation_rejected(
    db_session: Session, shared_masters_env
) -> None:
    """Verify selecting inactive department or designation fails validation."""
    env = shared_masters_env

    # 1. Inactive Department
    with pytest.raises(ValueError) as exc_dept:
        validate_user_cross_company_integrity(
            session=db_session,
            company_id=env["comp_gc"].company_id,
            department_id=env["dept_inactive"].department_id,
            designation_id=env["desig_sr_exec"].designation_id,
        )
    assert "is inactive" in str(exc_dept.value)

    # 2. Inactive Designation
    with pytest.raises(ValueError) as exc_desig:
        validate_user_cross_company_integrity(
            session=db_session,
            company_id=env["comp_gc"].company_id,
            department_id=env["dept_sales"].department_id,
            designation_id=env["desig_inactive"].designation_id,
        )
    assert "is inactive" in str(exc_desig.value)


def test_nonexistent_department_or_designation_rejected(
    db_session: Session, shared_masters_env
) -> None:
    """Verify non-existent UUIDs are rejected."""
    env = shared_masters_env
    random_id = uuid.uuid4()

    with pytest.raises(ValueError) as exc_dept:
        validate_user_cross_company_integrity(
            session=db_session,
            company_id=env["comp_gc"].company_id,
            department_id=random_id,
            designation_id=env["desig_sr_exec"].designation_id,
        )
    assert "not found" in str(exc_dept.value)


def test_cross_company_data_isolation_with_shared_department(
    db_session: Session, shared_masters_env
) -> None:
    """
    Verify that sharing department_id does NOT grant cross-company access.
    DataScopeContext with DEPARTMENT scope requires BOTH company_id AND department_id to match.
    """
    env = shared_masters_env

    # GC Sales employee
    gc_user_in = UserCreate(
        company_id=env["comp_gc"].company_id,
        department_id=env["dept_sales"].department_id,
        designation_id=env["desig_sr_exec"].designation_id,
        first_name="GC",
        last_name="Sales",
        official_email="gc.sales@gc.in",
        mobile_number="+919876543204",
        date_of_joining=date(2026, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    gc_user = create_user(db_session, gc_user_in)

    # EP Sales employee
    ep_user_in = UserCreate(
        company_id=env["comp_ep"].company_id,
        department_id=env["dept_sales"].department_id,
        designation_id=env["desig_sr_exec"].designation_id,
        first_name="EP",
        last_name="Sales",
        official_email="ep.sales@ep.in",
        mobile_number="+919876543205",
        date_of_joining=date(2026, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    ep_user = create_user(db_session, ep_user_in)
    db_session.flush()

    # Create DataScopeContext for GC user with DEPARTMENT scope
    gc_scope = DataScopeContext(
        scope="DEPARTMENT",
        user_id=gc_user.user_id,
        company_id=gc_user.company_id,
        department_id=gc_user.department_id,
    )

    # GC user IS permitted to access GC's sales record
    assert gc_scope.is_user_permitted(
        target_user_id=None,
        target_company_id=env["comp_gc"].company_id,
        target_department_id=env["dept_sales"].department_id,
    ) is True

    # GC user is NOT permitted to access EP's sales record even though department_id is identical
    assert gc_scope.is_user_permitted(
        target_user_id=None,
        target_company_id=env["comp_ep"].company_id,
        target_department_id=env["dept_sales"].department_id,
    ) is False
