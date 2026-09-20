"""Unit and integration tests for Secure First Super Admin Bootstrap CLI Script (Stage 10A)."""
import io
import uuid
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timezone
from typing import List, Optional
from unittest.mock import MagicMock, call, patch

import pytest
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.scripts.bootstrap_super_admin import (
    BootstrapError,
    build_cli_parser,
    execute_bootstrap_create,
    execute_bootstrap_promote,
    find_and_validate_company,
    find_and_validate_department,
    find_and_validate_designation,
    get_existing_super_admins,
    grant_all_module_permissions,
    main,
    prompt_for_password,
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def mock_session() -> MagicMock:
    """Mocked SQLAlchemy Session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def sample_company() -> Company:
    return Company(
        company_id=uuid.uuid4(),
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances",
        legal_name="Gocompliances Private Limited",
        employee_code_prefix="CG",
        next_employee_number=1,
        status="ACTIVE",
    )


@pytest.fixture
def sample_department(sample_company: Company) -> Department:
    return Department(
        department_id=uuid.uuid4(),
        company_id=sample_company.company_id,
        department_code="ADMINISTRATION",
        department_name="Administration",
        status="ACTIVE",
    )


@pytest.fixture
def sample_designation(sample_company: Company) -> Designation:
    return Designation(
        designation_id=uuid.uuid4(),
        company_id=sample_company.company_id,
        designation_code="DIRECTOR",
        designation_name="Director",
        status="ACTIVE",
    )


@pytest.fixture
def sample_modules() -> List[Module]:
    return [
        Module(
            module_id=uuid.uuid4(),
            module_code="ADMIN",
            module_name="Administration",
            parent_module_id=None,
            status="ACTIVE",
            display_order=1,
        ),
        Module(
            module_id=uuid.uuid4(),
            module_code="ADMIN_EMPLOYEES",
            module_name="Employees",
            parent_module_id=None,
            status="ACTIVE",
            display_order=2,
        ),
        Module(
            module_id=uuid.uuid4(),
            module_code="SALES",
            module_name="Sales",
            parent_module_id=None,
            status="ACTIVE",
            display_order=3,
        ),
    ]


# ==============================================================================
# CLI Argument Parser Tests
# ==============================================================================

def test_cli_parser_help() -> None:
    """Verify CLI parser generates help message without error."""
    parser = build_cli_parser()
    help_out = io.StringIO()
    with redirect_stdout(help_out):
        try:
            parser.parse_args(["--help"])
        except SystemExit:
            pass
    help_str = help_out.getvalue()
    assert "bootstrap_super_admin" in help_str
    assert "create" in help_str
    assert "promote" in help_str


def test_cli_parser_create_subcommand_arguments() -> None:
    """Verify argument parsing for create subcommand."""
    parser = build_cli_parser()
    args = parser.parse_args([
        "create",
        "--email", "admin@gocompliances.in",
        "--first-name", "Super",
        "--last-name", "Admin",
        "--phone", "9876543210",
        "--company-code", "CG",
        "--department-code", "ADMIN",
        "--designation-code", "DIRECTOR",
        "--joining-date", "2026-01-15",
        "--personal-email", "admin.personal@example.com",
        "--employment-type", "FULL_TIME",
        "--allow-additional-super-admin",
        "--update-existing-permissions",
        "--yes",
        "--dry-run",
    ])
    assert args.command == "create"
    assert args.email == "admin@gocompliances.in"
    assert args.first_name == "Super"
    assert args.last_name == "Admin"
    assert args.phone == "9876543210"
    assert args.company_code == "CG"
    assert args.department_code == "ADMIN"
    assert args.designation_code == "DIRECTOR"
    assert args.joining_date == date(2026, 1, 15)
    assert args.personal_email == "admin.personal@example.com"
    assert args.employment_type == "FULL_TIME"
    assert args.allow_additional_super_admin is True
    assert args.update_existing_permissions is True
    assert args.yes is True
    assert args.dry_run is True


def test_cli_parser_promote_subcommand_arguments() -> None:
    """Verify argument parsing for promote subcommand."""
    parser = build_cli_parser()
    args = parser.parse_args([
        "promote",
        "--employee-code", "CG0001",
        "--yes",
        "--dry-run",
    ])
    assert args.command == "promote"
    assert args.employee_code == "CG0001"
    assert args.yes is True
    assert args.dry_run is True


def test_cli_parser_missing_command_exits() -> None:
    """Verify main exits with error when no subcommand is provided."""
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 1


# ==============================================================================
# Password Prompt & Validation Tests
# ==============================================================================

def test_prompt_for_password_success() -> None:
    """Verify password prompting succeeds with matching valid strong password."""
    pw_inputs = iter(["SecureAdmin#2026!", "SecureAdmin#2026!"])
    pwd = prompt_for_password(password_getter=lambda prompt: next(pw_inputs))
    assert pwd == "SecureAdmin#2026!"


def test_prompt_for_password_mismatch_rejected() -> None:
    """Verify password prompting raises BootstrapError when confirmation differs."""
    pw_inputs = iter(["SecureAdmin#2026!", "DifferentAdmin#2026!"])
    with pytest.raises(BootstrapError) as exc:
        prompt_for_password(password_getter=lambda prompt: next(pw_inputs))
    assert "Password confirmation mismatch" in str(exc.value)


def test_prompt_for_password_complexity_rejected() -> None:
    """Verify password policy violation raises BootstrapError."""
    # Simple password lacking symbols/digits/length
    pw_inputs = iter(["weakpass", "weakpass"])
    with pytest.raises(BootstrapError) as exc:
        prompt_for_password(password_getter=lambda prompt: next(pw_inputs))
    assert "Password complexity validation failed" in str(exc.value)


# ==============================================================================
# Master Record Lookup & Validation Tests
# ==============================================================================

def test_find_and_validate_company_success(mock_session: MagicMock, sample_company: Company) -> None:
    """Verify company lookup by code or prefix."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_company
    found = find_and_validate_company(mock_session, "CG")
    assert found.company_id == sample_company.company_id
    assert found.company_code == "GOCOMPLIANCES"


def test_find_and_validate_company_not_found(mock_session: MagicMock) -> None:
    """Verify company lookup failure when code is not found."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(BootstrapError) as exc:
        find_and_validate_company(mock_session, "NONEXISTENT")
    assert "does not exist" in str(exc.value)


def test_find_and_validate_company_inactive(mock_session: MagicMock, sample_company: Company) -> None:
    """Verify inactive company is rejected."""
    sample_company.status = "INACTIVE"
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_company
    with pytest.raises(BootstrapError) as exc:
        find_and_validate_company(mock_session, "GOCOMPLIANCES")
    assert "is INACTIVE" in str(exc.value)


def test_find_and_validate_department_success(
    mock_session: MagicMock, sample_company: Company, sample_department: Department
) -> None:
    """Verify department lookup succeeds for active department within company."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_department
    found = find_and_validate_department(mock_session, sample_company.company_id, "ADMINISTRATION")
    assert found.department_id == sample_department.department_id


def test_find_and_validate_department_not_found_or_mismatch(
    mock_session: MagicMock, sample_company: Company
) -> None:
    """Verify department lookup fails when not found or mismatched with company."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(BootstrapError) as exc:
        find_and_validate_department(mock_session, sample_company.company_id, "UNKNOWN_DEPT")
    assert "does not exist for the selected company" in str(exc.value)


def test_find_and_validate_designation_success(
    mock_session: MagicMock, sample_company: Company, sample_designation: Designation
) -> None:
    """Verify designation lookup succeeds for active designation within company."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_designation
    found = find_and_validate_designation(mock_session, sample_company.company_id, "DIRECTOR")
    assert found.designation_id == sample_designation.designation_id


def test_find_and_validate_designation_inactive(
    mock_session: MagicMock, sample_company: Company, sample_designation: Designation
) -> None:
    """Verify inactive designation is rejected."""
    sample_designation.status = "INACTIVE"
    mock_session.execute.return_value.scalar_one_or_none.return_value = sample_designation
    with pytest.raises(BootstrapError) as exc:
        find_and_validate_designation(mock_session, sample_company.company_id, "DIRECTOR")
    assert "is INACTIVE" in str(exc.value)


# ==============================================================================
# Super Admin Detection & Permission Assignment Tests
# ==============================================================================

def test_get_existing_super_admins_none(mock_session: MagicMock) -> None:
    """Verify returns empty list when no super admin exists."""
    # Active modules exist, but query returns 0 users
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [uuid.uuid4(), uuid.uuid4()],  # active module ids
        [],  # users with full access
    ]
    admins = get_existing_super_admins(mock_session)
    assert admins == []


def test_get_existing_super_admins_found(mock_session: MagicMock) -> None:
    """Verify returns list of super admins."""
    admin_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        first_name="Existing",
        last_name="Admin",
        official_email="existing.admin@gocompliances.in",
        account_status="ACTIVE",
    )
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [uuid.uuid4()],  # active module ids
        [admin_user],    # super admin users
    ]
    admins = get_existing_super_admins(mock_session)
    assert len(admins) == 1
    assert admins[0].employee_code == "CG0001"


def test_grant_all_module_permissions_success(
    mock_session: MagicMock, sample_modules: List[Module]
) -> None:
    """Verify grant_all_module_permissions grants full ALL permissions across all active modules."""
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        sample_modules,  # active modules query
        [],              # existing perms query
    ]

    target_user_id = uuid.uuid4()
    with patch("app.scripts.bootstrap_super_admin.grant_or_update_permission") as mock_grant:
        count = grant_all_module_permissions(
            session=mock_session,
            user_id=target_user_id,
            update_existing_permissions=False,
        )
        assert count == 3
        assert mock_grant.call_count == 3
        # Ensure called with ALL data scope, self-granted, is_bootstrap=True
        for call_args in mock_grant.call_args_list:
            assert call_args.kwargs["data_scope"] == "ALL"
            assert call_args.kwargs["can_view"] is True
            assert call_args.kwargs["can_create"] is True
            assert call_args.kwargs["can_edit"] is True
            assert call_args.kwargs["can_delete"] is True
            assert call_args.kwargs["can_approve"] is True
            assert call_args.kwargs["status"] == "ACTIVE"
            assert call_args.kwargs["granted_by_user_id"] == target_user_id
            assert call_args.kwargs["is_bootstrap"] is True


def test_grant_all_module_permissions_conflict_without_flag(
    mock_session: MagicMock, sample_modules: List[Module]
) -> None:
    """Verify existing permissions without update flag raise BootstrapError."""
    existing_perm = UserModulePermission(
        permission_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        module_id=sample_modules[0].module_id,
        can_view=True,
    )
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        sample_modules,    # active modules query
        [existing_perm],   # existing perms query
    ]

    with pytest.raises(BootstrapError) as exc:
        grant_all_module_permissions(
            session=mock_session,
            user_id=uuid.uuid4(),
            update_existing_permissions=False,
        )
    assert "Permission records already exist" in str(exc.value)
    assert "--update-existing-permissions" in str(exc.value)


def test_grant_all_module_permissions_with_update_flag(
    mock_session: MagicMock, sample_modules: List[Module]
) -> None:
    """Verify existing permissions are updated when update flag is provided."""
    existing_perm = UserModulePermission(
        permission_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        module_id=sample_modules[0].module_id,
        can_view=True,
    )
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        sample_modules,
        [existing_perm],
    ]

    with patch("app.scripts.bootstrap_super_admin.grant_or_update_permission") as mock_grant:
        count = grant_all_module_permissions(
            session=mock_session,
            user_id=uuid.uuid4(),
            update_existing_permissions=True,
        )
        assert count == 3
        assert mock_grant.call_count == 3


# ==============================================================================
# Mode 1: Create New Super Admin Tests
# ==============================================================================

def test_execute_bootstrap_create_success(
    mock_session: MagicMock,
    sample_company: Company,
    sample_department: Department,
    sample_designation: Designation,
    sample_modules: List[Module],
) -> None:
    """Verify successful creation of a new Super Admin employee."""
    # Setup queries:
    # 1. Email check -> None
    # 2. Company lookup -> sample_company
    # 3. Department lookup -> sample_department
    # 4. Designation lookup -> sample_designation
    # 5. Super Admin check -> []
    # 6. Active modules query -> sample_modules
    # 7. grant_all_module_permissions queries -> sample_modules, []
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        None,                 # email check
        sample_company,       # company
        sample_department,    # department
        sample_designation,   # designation
    ]
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules],  # get_existing_super_admins active modules
        [],                                     # get_existing_super_admins users
        sample_modules,                         # summary active modules
        sample_modules,                         # grant_all_module_permissions active modules
        [],                                     # grant_all_module_permissions existing perms
    ]

    pw_inputs = iter(["SuperSecureAdmin#2026!", "SuperSecureAdmin#2026!"])

    with patch("app.scripts.bootstrap_super_admin.generate_employee_code", return_value="CG0001"), \
         patch("app.scripts.bootstrap_super_admin.grant_or_update_permission"):

        created_user = execute_bootstrap_create(
            session=mock_session,
            email="superadmin@gocompliances.in",
            first_name="Super",
            last_name="Administrator",
            middle_name=None,
            phone="9876543210",
            company_code="CG",
            department_code="ADMINISTRATION",
            designation_code="DIRECTOR",
            joining_date=date(2026, 1, 1),
            auto_confirm=True,
            password_getter=lambda p: next(pw_inputs),
        )

        assert created_user.employee_code == "CG0001"
        assert created_user.official_email == "superadmin@gocompliances.in"
        assert created_user.account_status == "ACTIVE"
        assert created_user.password_hash is not None
        assert verify_password("SuperSecureAdmin#2026!", created_user.password_hash) is True
        assert mock_session.commit.called is True


def test_execute_bootstrap_create_dry_run_makes_no_db_changes(
    mock_session: MagicMock,
    sample_company: Company,
    sample_department: Department,
    sample_designation: Designation,
    sample_modules: List[Module],
) -> None:
    """Verify dry-run mode does not commit to database and does not prompt for password."""
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        None,                 # email check
        sample_company,       # company
        sample_department,    # department
        sample_designation,   # designation
    ]
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules],  # super admin check
        [],                                     # no super admins
        sample_modules,                         # active modules for summary
    ]

    pw_getter_mock = MagicMock()

    dry_user = execute_bootstrap_create(
        session=mock_session,
        email="superadmin@gocompliances.in",
        first_name="Super",
        last_name="Administrator",
        middle_name=None,
        phone="9876543210",
        company_code="CG",
        department_code="ADMINISTRATION",
        designation_code="DIRECTOR",
        dry_run=True,
        password_getter=pw_getter_mock,
    )

    assert dry_user.official_email == "superadmin@gocompliances.in"
    assert pw_getter_mock.called is False
    assert mock_session.add.called is False
    assert mock_session.commit.called is False


def test_execute_bootstrap_create_duplicate_email_rejected(
    mock_session: MagicMock,
) -> None:
    """Verify duplicate official email is rejected."""
    existing_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        official_email="admin@gocompliances.in",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = existing_user

    with pytest.raises(BootstrapError) as exc:
        execute_bootstrap_create(
            session=mock_session,
            email="admin@gocompliances.in",
            first_name="Super",
            last_name="Admin",
            middle_name=None,
            phone="9876543210",
            company_code="CG",
            department_code="ADMINISTRATION",
            designation_code="DIRECTOR",
            auto_confirm=True,
        )
    assert "already registered in user_master" in str(exc.value)


def test_execute_bootstrap_create_blocked_by_existing_super_admin(
    mock_session: MagicMock,
    sample_company: Company,
    sample_department: Department,
    sample_designation: Designation,
    sample_modules: List[Module],
) -> None:
    """Verify creation is blocked if another active Super Admin exists and allow flag is not passed."""
    existing_admin = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        first_name="First",
        last_name="Admin",
        official_email="first.admin@gocompliances.in",
        account_status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        None,                 # email check
        sample_company,       # company
        sample_department,    # department
        sample_designation,   # designation
    ]
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules],  # active module ids
        [existing_admin],                       # existing super admin found!
    ]

    with pytest.raises(BootstrapError) as exc:
        execute_bootstrap_create(
            session=mock_session,
            email="second.admin@gocompliances.in",
            first_name="Second",
            last_name="Admin",
            middle_name=None,
            phone="9876543210",
            company_code="CG",
            department_code="ADMINISTRATION",
            designation_code="DIRECTOR",
            allow_additional_super_admin=False,
            auto_confirm=True,
        )
    assert "Super Admin account already exists" in str(exc.value)
    assert "--allow-additional-super-admin" in str(exc.value)


def test_execute_bootstrap_create_allowed_with_additional_super_admin_flag(
    mock_session: MagicMock,
    sample_company: Company,
    sample_department: Department,
    sample_designation: Designation,
    sample_modules: List[Module],
) -> None:
    """Verify creation proceeds when allow_additional_super_admin=True."""
    existing_admin = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        first_name="First",
        last_name="Admin",
        official_email="first.admin@gocompliances.in",
        account_status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        None,                 # email check
        sample_company,       # company
        sample_department,    # department
        sample_designation,   # designation
    ]
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules],  # active module ids
        [existing_admin],                       # existing super admin
        sample_modules,                         # summary modules
        sample_modules,                         # grant modules
        [],                                     # grant existing perms
    ]

    pw_inputs = iter(["SuperSecureAdmin#2026!", "SuperSecureAdmin#2026!"])

    with patch("app.scripts.bootstrap_super_admin.generate_employee_code", return_value="CG0002"), \
         patch("app.scripts.bootstrap_super_admin.grant_or_update_permission"):

        created = execute_bootstrap_create(
            session=mock_session,
            email="second.admin@gocompliances.in",
            first_name="Second",
            last_name="Admin",
            middle_name=None,
            phone="9876543210",
            company_code="CG",
            department_code="ADMINISTRATION",
            designation_code="DIRECTOR",
            allow_additional_super_admin=True,
            auto_confirm=True,
            password_getter=lambda p: next(pw_inputs),
        )
        assert created.employee_code == "CG0002"


def test_execute_bootstrap_create_confirmation_mismatch_aborts(
    mock_session: MagicMock,
    sample_company: Company,
    sample_department: Department,
    sample_designation: Designation,
    sample_modules: List[Module],
) -> None:
    """Verify typing incorrect confirmation aborts creation."""
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        None, sample_company, sample_department, sample_designation
    ]
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules], [], sample_modules
    ]

    pw_inputs = iter(["SuperSecureAdmin#2026!", "SuperSecureAdmin#2026!"])

    with pytest.raises(BootstrapError) as exc:
        execute_bootstrap_create(
            session=mock_session,
            email="admin@gocompliances.in",
            first_name="Super",
            last_name="Admin",
            middle_name=None,
            phone="9876543210",
            company_code="CG",
            department_code="ADMINISTRATION",
            designation_code="DIRECTOR",
            auto_confirm=False,
            password_getter=lambda p: next(pw_inputs),
            input_getter=lambda prompt: "NO",
        )
    assert "Operation aborted by user" in str(exc.value)


def test_execute_bootstrap_create_rollback_on_db_exception(
    mock_session: MagicMock,
    sample_company: Company,
    sample_department: Department,
    sample_designation: Designation,
    sample_modules: List[Module],
) -> None:
    """Verify transaction rollback occurs if exception happens during DB commit."""
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        None, sample_company, sample_department, sample_designation
    ]
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules], [], sample_modules, sample_modules, []
    ]
    mock_session.commit.side_effect = RuntimeError("DB connection dropped")

    pw_inputs = iter(["SuperSecureAdmin#2026!", "SuperSecureAdmin#2026!"])

    with patch("app.scripts.bootstrap_super_admin.generate_employee_code", return_value="CG0001"), \
         patch("app.scripts.bootstrap_super_admin.grant_or_update_permission"):

        with pytest.raises(BootstrapError) as exc:
            execute_bootstrap_create(
                session=mock_session,
                email="admin@gocompliances.in",
                first_name="Super",
                last_name="Admin",
                middle_name=None,
                phone="9876543210",
                company_code="CG",
                department_code="ADMINISTRATION",
                designation_code="DIRECTOR",
                auto_confirm=True,
                password_getter=lambda p: next(pw_inputs),
            )
        assert "Database transaction failed" in str(exc.value)
        assert mock_session.rollback.called is True


# ==============================================================================
# Mode 2: Promote Existing Employee Tests
# ==============================================================================

def test_execute_bootstrap_promote_success_with_existing_password(
    mock_session: MagicMock,
    sample_modules: List[Module],
) -> None:
    """Verify promotion of an active employee who already has a password."""
    existing_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        first_name="Existing",
        last_name="Employee",
        official_email="emp@gocompliances.in",
        account_status="ACTIVE",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$dummyhash",
    )

    # 1. User lookup -> existing_user
    mock_session.execute.return_value.scalar_one_or_none.return_value = existing_user
    # 2. Super admin check -> active module ids, no other super admin
    # 3. Active modules for summary
    # 4. grant_all_module_permissions -> active modules, []
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules],
        [],
        sample_modules,
        sample_modules,
        [],
    ]

    pw_getter_mock = MagicMock()

    with patch("app.scripts.bootstrap_super_admin.grant_or_update_permission"):
        promoted = execute_bootstrap_promote(
            session=mock_session,
            email="emp@gocompliances.in",
            auto_confirm=True,
            password_getter=pw_getter_mock,
        )

        assert promoted.employee_code == "CG0001"
        assert promoted.password_hash == "$argon2id$v=19$m=65536,t=3,p=4$dummyhash"
        # Since password exists, password_getter should NOT be called
        assert pw_getter_mock.called is False
        assert mock_session.commit.called is True


def test_execute_bootstrap_promote_sets_initial_password_when_none(
    mock_session: MagicMock,
    sample_modules: List[Module],
) -> None:
    """Verify promotion sets initial password when employee does not have credentials."""
    existing_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        first_name="Existing",
        last_name="Employee",
        official_email="emp@gocompliances.in",
        account_status="ACTIVE",
        password_hash=None,
    )

    mock_session.execute.return_value.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules],
        [],
        sample_modules,
        sample_modules,
        [],
    ]

    pw_inputs = iter(["InitialPass#2026!", "InitialPass#2026!"])

    with patch("app.scripts.bootstrap_super_admin.grant_or_update_permission"):
        promoted = execute_bootstrap_promote(
            session=mock_session,
            employee_code="CG0001",
            auto_confirm=True,
            password_getter=lambda p: next(pw_inputs),
        )

        assert promoted.employee_code == "CG0001"
        assert promoted.password_hash is not None
        assert verify_password("InitialPass#2026!", promoted.password_hash) is True
        assert mock_session.commit.called is True


def test_execute_bootstrap_promote_inactive_employee_rejected(
    mock_session: MagicMock,
) -> None:
    """Verify promoting inactive employee raises BootstrapError."""
    inactive_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        official_email="inactive@gocompliances.in",
        account_status="INACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = inactive_user

    with pytest.raises(BootstrapError) as exc:
        execute_bootstrap_promote(
            session=mock_session,
            email="inactive@gocompliances.in",
            auto_confirm=True,
        )
    assert "has account_status 'INACTIVE'" in str(exc.value)


def test_execute_bootstrap_promote_nonexistent_employee_rejected(
    mock_session: MagicMock,
) -> None:
    """Verify promoting non-existent employee raises BootstrapError."""
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(BootstrapError) as exc:
        execute_bootstrap_promote(
            session=mock_session,
            employee_code="CG9999",
            auto_confirm=True,
        )
    assert "was not found in user_master" in str(exc.value)


def test_execute_bootstrap_promote_dry_run_makes_no_mutations(
    mock_session: MagicMock,
    sample_modules: List[Module],
) -> None:
    """Verify dry-run mode in promote does not mutate employee or permissions."""
    existing_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        official_email="emp@gocompliances.in",
        account_status="ACTIVE",
        password_hash=None,
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules],
        [],
        sample_modules,
    ]

    pw_getter_mock = MagicMock()

    dry_user = execute_bootstrap_promote(
        session=mock_session,
        email="emp@gocompliances.in",
        dry_run=True,
        password_getter=pw_getter_mock,
    )

    assert dry_user.employee_code == "CG0001"
    assert pw_getter_mock.called is False
    assert mock_session.commit.called is False


# ==============================================================================
# Security & Secret Sanitization Tests
# ==============================================================================

def test_no_plaintext_passwords_or_hashes_in_stdout(
    mock_session: MagicMock,
    sample_company: Company,
    sample_department: Department,
    sample_designation: Designation,
    sample_modules: List[Module],
) -> None:
    """Verify that stdout never prints plaintext passwords or Argon2 hashes."""
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        None, sample_company, sample_department, sample_designation
    ]
    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [m.module_id for m in sample_modules], [], sample_modules, sample_modules, []
    ]

    pw = "SuperSecret#Admin2026!"
    pw_inputs = iter([pw, pw])

    stdout_capture = io.StringIO()
    with redirect_stdout(stdout_capture):
        with patch("app.scripts.bootstrap_super_admin.generate_employee_code", return_value="CG0001"), \
             patch("app.scripts.bootstrap_super_admin.grant_or_update_permission"):

            created = execute_bootstrap_create(
                session=mock_session,
                email="admin@gocompliances.in",
                first_name="Super",
                last_name="Admin",
                middle_name=None,
                phone="9876543210",
                company_code="CG",
                department_code="ADMINISTRATION",
                designation_code="DIRECTOR",
                auto_confirm=True,
                password_getter=lambda p: next(pw_inputs),
            )

    output = stdout_capture.getvalue()
    assert pw not in output
    assert "$argon2id$" not in output
    assert created.password_hash is not None
    assert "$argon2id$" in created.password_hash
