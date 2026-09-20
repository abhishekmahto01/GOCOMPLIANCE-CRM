"""Unit and integration tests for Data Scope Resolution and Hierarchy CTE."""
import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.permissions import (
    DataScopeContext,
    PermissionDeniedError,
    get_effective_scope,
    get_team_user_ids,
    resolve_data_scope_context,
)


def test_data_scope_context_is_user_permitted() -> None:
    """Verify DataScopeContext evaluation rules for SELF, TEAM, DEPARTMENT, COMPANY, and ALL."""
    user_id = uuid.uuid4()
    company_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    other_company_id = uuid.uuid4()
    other_dept_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    subordinate_id = uuid.uuid4()

    # 1. SELF scope
    self_ctx = DataScopeContext(
        scope="SELF",
        user_id=user_id,
        company_id=company_id,
        department_id=dept_id,
        team_user_ids=[user_id],
    )
    assert self_ctx.is_user_permitted(user_id) is True
    assert self_ctx.is_user_permitted(other_user_id) is False

    # 2. TEAM scope
    team_ctx = DataScopeContext(
        scope="TEAM",
        user_id=user_id,
        company_id=company_id,
        department_id=dept_id,
        team_user_ids=[user_id, subordinate_id],
    )
    assert team_ctx.is_user_permitted(user_id) is True
    assert team_ctx.is_user_permitted(subordinate_id) is True
    assert team_ctx.is_user_permitted(other_user_id) is False

    # 3. DEPARTMENT scope
    dept_ctx = DataScopeContext(
        scope="DEPARTMENT",
        user_id=user_id,
        company_id=company_id,
        department_id=dept_id,
    )
    # Same company and same department
    assert dept_ctx.is_user_permitted(other_user_id, company_id, dept_id) is True
    # Different department in same company
    assert dept_ctx.is_user_permitted(other_user_id, company_id, other_dept_id) is False
    # Same department name but different company
    assert dept_ctx.is_user_permitted(other_user_id, other_company_id, dept_id) is False

    # 4. COMPANY scope
    comp_ctx = DataScopeContext(
        scope="COMPANY",
        user_id=user_id,
        company_id=company_id,
        department_id=dept_id,
    )
    assert comp_ctx.is_user_permitted(other_user_id, company_id, other_dept_id) is True
    assert comp_ctx.is_user_permitted(other_user_id, other_company_id, dept_id) is False

    # 5. ALL scope
    all_ctx = DataScopeContext(
        scope="ALL",
        user_id=user_id,
        company_id=company_id,
        department_id=dept_id,
    )
    assert all_ctx.is_user_permitted(other_user_id, other_company_id, other_dept_id) is True


def test_get_team_user_ids_recursive_cte_mock() -> None:
    """Verify that get_team_user_ids queries the recursive subordinates CTE."""
    mock_session = MagicMock(spec=Session)
    manager_id = uuid.uuid4()
    sub_1 = uuid.uuid4()
    sub_2 = uuid.uuid4()

    mock_session.execute.return_value.fetchall.return_value = [
        (manager_id,),
        (sub_1,),
        (sub_2,),
    ]

    result = get_team_user_ids(mock_session, manager_id)
    assert result == [manager_id, sub_1, sub_2]

    # Verify query passed manager_id
    call_args = mock_session.execute.call_args
    assert "WITH RECURSIVE subordinates AS" in str(call_args[0][0])
    assert call_args[0][1]["root_id"] == manager_id


def test_resolve_data_scope_context_team() -> None:
    """Verify resolve_data_scope_context fetches team subordinates when scope is TEAM."""
    mock_session = MagicMock(spec=Session)
    user_id = uuid.uuid4()
    company_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    subordinate_id = uuid.uuid4()

    mock_user = MagicMock(
        spec=User,
        user_id=user_id,
        company_id=company_id,
        department_id=dept_id,
        employee_code="CG0001",
        account_status="ACTIVE",
    )

    with patch("app.services.permissions.get_effective_scope", return_value="TEAM"), \
         patch("app.services.permissions.get_team_user_ids", return_value=[user_id, subordinate_id]):
        ctx = resolve_data_scope_context(mock_session, mock_user, "SALES")
        assert ctx.scope == "TEAM"
        assert ctx.user_id == user_id
        assert ctx.company_id == company_id
        assert ctx.department_id == dept_id
        assert ctx.team_user_ids == [user_id, subordinate_id]


def test_resolve_data_scope_context_denied_when_no_view() -> None:
    """Verify resolve_data_scope_context raises PermissionDeniedError when effective scope is None."""
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock(
        spec=User,
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        account_status="ACTIVE",
    )

    with patch("app.services.permissions.get_effective_scope", return_value=None):
        with pytest.raises(PermissionDeniedError) as exc:
            resolve_data_scope_context(mock_session, mock_user, "SALES")
        assert "has no view access" in str(exc.value)


def test_recursive_cte_hierarchy_and_cycle_safety_in_db() -> None:
    """Integration test verifying CTE recursive hierarchy and cycle safety against PostgreSQL."""
    from datetime import date
    from app.database.session import SessionLocal
    from app.models.company import Company
    from app.models.department import Department
    from app.models.designation import Designation

    with SessionLocal() as db:
        try:
            # Query existing seeded masters
            company = db.query(Company).first()
            department = db.query(Department).filter_by(company_id=company.company_id).first()
            designation = db.query(Designation).filter_by(company_id=company.company_id).first()

            assert company is not None
            assert department is not None
            assert designation is not None

            # Create hierarchy: Director (u1) -> Manager (u2) -> Lead (u3) -> Exec (u4)
            # And an unrelated peer (u5) with no manager or subordinate relation
            u1_id, u2_id, u3_id, u4_id, u5_id = [uuid.uuid4() for _ in range(5)]

            u1 = User(
                user_id=u1_id,
                employee_code="CG9001",
                company_id=company.company_id,
                department_id=department.department_id,
                designation_id=designation.designation_id,
                manager_user_id=None,
                first_name="Director",
                last_name="One",
                official_email="dir1@test.internal",
                mobile_number="+919900000001",
                date_of_joining=date(2026, 1, 1),
                employment_type="FULL_TIME",
                account_status="ACTIVE",
            )
            u2 = User(
                user_id=u2_id,
                employee_code="CG9002",
                company_id=company.company_id,
                department_id=department.department_id,
                designation_id=designation.designation_id,
                manager_user_id=u1_id,
                first_name="Manager",
                last_name="Two",
                official_email="mgr2@test.internal",
                mobile_number="+919900000002",
                date_of_joining=date(2026, 1, 1),
                employment_type="FULL_TIME",
                account_status="ACTIVE",
            )
            u3 = User(
                user_id=u3_id,
                employee_code="CG9003",
                company_id=company.company_id,
                department_id=department.department_id,
                designation_id=designation.designation_id,
                manager_user_id=u2_id,
                first_name="Lead",
                last_name="Three",
                official_email="lead3@test.internal",
                mobile_number="+919900000003",
                date_of_joining=date(2026, 1, 1),
                employment_type="FULL_TIME",
                account_status="ACTIVE",
            )
            u4 = User(
                user_id=u4_id,
                employee_code="CG9004",
                company_id=company.company_id,
                department_id=department.department_id,
                designation_id=designation.designation_id,
                manager_user_id=u3_id,
                first_name="Exec",
                last_name="Four",
                official_email="exec4@test.internal",
                mobile_number="+919900000004",
                date_of_joining=date(2026, 1, 1),
                employment_type="FULL_TIME",
                account_status="ACTIVE",
            )
            u5 = User(
                user_id=u5_id,
                employee_code="CG9005",
                company_id=company.company_id,
                department_id=department.department_id,
                designation_id=designation.designation_id,
                manager_user_id=None,
                first_name="Peer",
                last_name="Five",
                official_email="peer5@test.internal",
                mobile_number="+919900000005",
                date_of_joining=date(2026, 1, 1),
                employment_type="FULL_TIME",
                account_status="ACTIVE",
            )

            db.add_all([u1, u2, u3, u4, u5])
            db.flush()

            # 1. Director team: u1, u2, u3, u4 (excludes u5)
            dir_team = get_team_user_ids(db, u1_id)
            assert set(dir_team) == {u1_id, u2_id, u3_id, u4_id}
            assert u5_id not in dir_team

            # 2. Manager team: u2, u3, u4 (excludes u1 and u5)
            mgr_team = get_team_user_ids(db, u2_id)
            assert set(mgr_team) == {u2_id, u3_id, u4_id}
            assert u1_id not in mgr_team

            # 3. Exec team (leaf): only u4
            exec_team = get_team_user_ids(db, u4_id)
            assert set(exec_team) == {u4_id}

            # 4. Cycle test: simulate circular hierarchy u1 -> u2 -> u3 -> u1
            # Update u1's manager to u3 to create an intentional cycle
            u1.manager_user_id = u3_id
            db.flush()

            # Cycle must not hang or infinite loop! CTE path tracking should terminate safely.
            cycle_team = get_team_user_ids(db, u1_id)
            assert set(cycle_team) == {u1_id, u2_id, u3_id, u4_id}

        finally:
            # Always rollback test transaction so DB remains clean at 0 users
            db.rollback()
