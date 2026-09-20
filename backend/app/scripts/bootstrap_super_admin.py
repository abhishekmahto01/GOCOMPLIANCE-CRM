"""Secure First Super Admin Bootstrap CLI Script (Stage 10A).

This utility provides an explicit command-line interface to bootstrap the first Super Admin
account or promote an existing employee with full ALL permissions across all active modules.

Security Safeguards:
- CLI execution only; no HTTP exposure.
- Zero hardcoded/default credentials.
- Passwords prompted securely via getpass (never logged or printed).
- Password policy enforced via Argon2 password hashing.
- Full ALL data scope and all action flags (view, create, edit, delete, approve) granted across all active modules.
- Existing Super Admin safety guard prevents accidental creation of duplicate unrestricted accounts.
- Atomic transaction with complete rollback on any failure.
- Dry-run mode for pre-flight validation without database mutations.
"""
import argparse
import getpass
import re
import sys
import uuid
from datetime import date, datetime, timezone
from typing import Callable, List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, validate_password_strength
from app.database.session import SessionLocal
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.user import normalize_email_address, normalize_mobile
from app.services.employee_code import generate_employee_code
from app.services.permissions import grant_or_update_permission


class BootstrapError(Exception):
    """Domain exception raised during Super Admin bootstrap validation or execution."""
    pass


def get_existing_super_admins(session: Session) -> List[User]:
    """Find all active users who already possess full ALL access to every active module.

    A user is considered a Super Admin if they have active UserModulePermission records
    with data_scope='ALL' and all action flags (view, create, edit, delete, approve) enabled
    for 100% of the active modules in module_master.
    """
    active_module_ids = session.execute(
        select(Module.module_id).where(Module.status == "ACTIVE")
    ).scalars().all()

    if not active_module_ids:
        return []

    total_active_modules = len(active_module_ids)
    now_utc = datetime.now(timezone.utc)

    stmt = (
        select(User)
        .join(UserModulePermission, User.user_id == UserModulePermission.user_id)
        .where(
            User.account_status == "ACTIVE",
            UserModulePermission.module_id.in_(active_module_ids),
            UserModulePermission.status == "ACTIVE",
            UserModulePermission.can_view.is_(True),
            UserModulePermission.can_create.is_(True),
            UserModulePermission.can_edit.is_(True),
            UserModulePermission.can_delete.is_(True),
            UserModulePermission.can_approve.is_(True),
            UserModulePermission.data_scope == "ALL",
            or_(
                UserModulePermission.expires_at.is_(None),
                UserModulePermission.expires_at > now_utc,
            ),
        )
        .group_by(User.user_id)
        .having(func.count(UserModulePermission.module_id) == total_active_modules)
    )
    return session.execute(stmt).scalars().all()


def find_and_validate_company(session: Session, company_code: str) -> Company:
    """Find and validate active Company by code or employee prefix."""
    code_norm = company_code.strip().upper()
    company = session.execute(
        select(Company).where(
            or_(
                func.upper(Company.company_code) == code_norm,
                func.upper(Company.employee_code_prefix) == code_norm,
            )
        )
    ).scalar_one_or_none()

    if not company:
        raise BootstrapError(f"Company '{company_code}' does not exist.")
    if company.status != "ACTIVE":
        raise BootstrapError(f"Company '{company.company_name}' ({company.company_code}) is INACTIVE.")
    return company


def find_and_validate_department(
    session: Session, company_id: uuid.UUID, department_code: str
) -> Department:
    """Find and validate active Department belonging to target company."""
    dept_norm = department_code.strip().upper()
    dept = session.execute(
        select(Department).where(
            Department.company_id == company_id,
            or_(
                func.upper(Department.department_code) == dept_norm,
                func.upper(Department.department_name) == dept_norm,
            ),
        )
    ).scalar_one_or_none()

    if not dept:
        raise BootstrapError(
            f"Department '{department_code}' does not exist for the selected company."
        )
    if dept.status != "ACTIVE":
        raise BootstrapError(f"Department '{dept.department_name}' is INACTIVE.")
    return dept


def find_and_validate_designation(
    session: Session, company_id: uuid.UUID, designation_code: str
) -> Designation:
    """Find and validate active Designation belonging to target company."""
    desig_norm = designation_code.strip().upper()
    desig = session.execute(
        select(Designation).where(
            Designation.company_id == company_id,
            or_(
                func.upper(Designation.designation_code) == desig_norm,
                func.upper(Designation.designation_name) == desig_norm,
            ),
        )
    ).scalar_one_or_none()

    if not desig:
        raise BootstrapError(
            f"Designation '{designation_code}' does not exist for the selected company."
        )
    if desig.status != "ACTIVE":
        raise BootstrapError(f"Designation '{desig.designation_name}' is INACTIVE.")
    return desig


def prompt_for_password(
    password_getter: Callable[[str], str] = getpass.getpass,
) -> str:
    """Prompt operator securely for initial password with confirmation and policy check."""
    print("\nEnter initial password for the Super Admin account:")
    pwd = password_getter("Password: ")
    confirm_pwd = password_getter("Confirm Password: ")

    if pwd != confirm_pwd:
        raise BootstrapError("Password confirmation mismatch. The entered passwords do not match.")

    try:
        validate_password_strength(pwd)
    except ValueError as val_err:
        raise BootstrapError(f"Password complexity validation failed: {val_err}")

    return pwd


def grant_all_module_permissions(
    session: Session,
    user_id: uuid.UUID,
    update_existing_permissions: bool,
) -> int:
    """Grant full ALL access on every active module.

    Raises:
        BootstrapError: If no active modules exist or if unflagged permission conflicts are encountered.
    """
    active_modules = session.execute(
        select(Module).where(Module.status == "ACTIVE").order_by(Module.display_order.asc())
    ).scalars().all()

    if not active_modules:
        raise BootstrapError(
            "No active modules found in module_master. Please execute 'seed_modules' before bootstrapping."
        )

    # Check for existing permissions if update flag is not set
    existing_perms = session.execute(
        select(UserModulePermission).where(
            UserModulePermission.user_id == user_id,
            UserModulePermission.module_id.in_([m.module_id for m in active_modules]),
        )
    ).scalars().all()

    if existing_perms and not update_existing_permissions:
        existing_mod_ids = {p.module_id for p in existing_perms}
        conflict_codes = [m.module_code for m in active_modules if m.module_id in existing_mod_ids]
        raise BootstrapError(
            f"Permission records already exist for module(s): {', '.join(conflict_codes)}. "
            f"Specify --update-existing-permissions to update existing permissions intentionally."
        )

    granted_count = 0
    for mod in active_modules:
        grant_or_update_permission(
            session=session,
            user_id=user_id,
            module_id=mod.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            data_scope="ALL",
            status="ACTIVE",
            granted_by_user_id=user_id,
            is_bootstrap=True,
        )
        granted_count += 1

    return granted_count


def execute_bootstrap_create(
    session: Session,
    email: str,
    first_name: str,
    last_name: str,
    middle_name: Optional[str],
    phone: str,
    company_code: str,
    department_code: str,
    designation_code: str,
    joining_date: Optional[date] = None,
    personal_email: Optional[str] = None,
    employment_type: str = "FULL_TIME",
    allow_additional_super_admin: bool = False,
    update_existing_permissions: bool = False,
    auto_confirm: bool = False,
    dry_run: bool = False,
    password_getter: Callable[[str], str] = getpass.getpass,
    input_getter: Callable[[str], str] = input,
) -> User:
    """Execute Mode 1: Create a new Super Admin employee."""
    # 1. Normalize and validate inputs
    email_clean = normalize_email_address(email, "official_email")
    phone_clean = normalize_mobile(phone)
    p_email_clean = normalize_email_address(personal_email, "personal_email") if personal_email else None
    join_dt = joining_date or date.today()

    # 2. Check email uniqueness
    existing = session.execute(
        select(User).where(func.lower(User.official_email) == email_clean)
    ).scalar_one_or_none()
    if existing:
        raise BootstrapError(f"Official email '{email_clean}' is already registered in user_master.")

    # 3. Master records lookup & validation
    company = find_and_validate_company(session, company_code)
    department = find_and_validate_department(session, company.company_id, department_code)
    designation = find_and_validate_designation(session, company.company_id, designation_code)

    # 4. Super Admin Safety Check
    existing_super_admins = get_existing_super_admins(session)
    if existing_super_admins and not allow_additional_super_admin:
        admin_summaries = ", ".join(
            f"{a.employee_code} ({a.first_name} {a.last_name}, {a.official_email})"
            for a in existing_super_admins
        )
        raise BootstrapError(
            f"Super Admin account already exists: {admin_summaries}. "
            f"To create an additional unrestricted Super Admin, pass --allow-additional-super-admin."
        )

    # 5. Fetch active modules for summary
    active_modules = session.execute(
        select(Module).where(Module.status == "ACTIVE").order_by(Module.display_order.asc())
    ).scalars().all()
    if not active_modules:
        raise BootstrapError("No active modules found in module_master. Run seed_modules first.")

    # 6. Display Safe Summary
    print("\n" + "=" * 72)
    print("GOCOMPLIANCE CRM - SUPER ADMIN BOOTSTRAP SUMMARY (CREATE MODE)")
    print("=" * 72)
    print(f"Operation Type     : CREATE NEW SUPER ADMIN")
    print(f"Employee Name      : {first_name} {middle_name + ' ' if middle_name else ''}{last_name}")
    print(f"Official Email     : {email_clean}")
    print(f"Mobile Number      : {phone_clean}")
    print(f"Company            : {company.company_name} ({company.company_code})")
    print(f"Department         : {department.department_name} ({department.department_code})")
    print(f"Designation        : {designation.designation_name} ({designation.designation_code})")
    print(f"Date of Joining    : {join_dt}")
    print(f"Assigned Data Scope: ALL (Unrestricted across all companies)")
    print(f"Action Rights      : VIEW, CREATE, EDIT, DELETE, APPROVE (Full)")
    print(f"Active Modules ({len(active_modules)}): {', '.join(m.module_code for m in active_modules)}")
    print("=" * 72)

    if dry_run:
        print("\n[DRY-RUN] Pre-flight validation successful. No database changes made. Password not prompted.")
        return User(
            user_id=uuid.uuid4(),
            employee_code=f"{company.employee_code_prefix}DRY",
            first_name=first_name,
            last_name=last_name,
            official_email=email_clean,
            mobile_number=phone_clean,
            company_id=company.company_id,
            department_id=department.department_id,
            designation_id=designation.designation_id,
            date_of_joining=join_dt,
            employment_type=employment_type,
            account_status="ACTIVE",
        )

    # 7. Prompt Password
    password = prompt_for_password(password_getter=password_getter)
    pw_hash = hash_password(password)

    # 8. Confirmation Prompt
    if not auto_confirm:
        print("\nType 'CREATE SUPER ADMIN' to proceed with account creation and permission grant:")
        conf = input_getter("Confirmation: ").strip()
        if conf != "CREATE SUPER ADMIN":
            raise BootstrapError("Operation aborted by user. Confirmation mismatch.")

    # 9. Atomic Transaction
    try:
        employee_code = generate_employee_code(session, company.company_id)
        user = User(
            user_id=uuid.uuid4(),
            employee_code=employee_code,
            company_id=company.company_id,
            department_id=department.department_id,
            designation_id=designation.designation_id,
            manager_user_id=None,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            official_email=email_clean,
            personal_email=p_email_clean,
            mobile_number=phone_clean,
            date_of_joining=join_dt,
            employment_type=employment_type,
            account_status="ACTIVE",
            password_hash=pw_hash,
            must_change_password=False,
        )
        session.add(user)
        session.flush()

        grant_count = grant_all_module_permissions(
            session=session,
            user_id=user.user_id,
            update_existing_permissions=update_existing_permissions,
        )
        session.commit()
        session.refresh(user)

        print("\n" + "=" * 72)
        print("SUPER ADMIN CREATED SUCCESSFULLY")
        print("=" * 72)
        print(f"Employee Code : {user.employee_code}")
        print(f"Official Email: {user.official_email}")
        print(f"Name          : {user.first_name} {user.last_name}")
        print(f"Permissions   : {grant_count} active modules assigned with 'ALL' data scope.")
        print(f"Status        : ACTIVE (Ready to log in at http://localhost:8001)")
        print("=" * 72)
        return user

    except Exception as exc:
        session.rollback()
        raise BootstrapError(f"Database transaction failed during Super Admin creation: {exc}")


def execute_bootstrap_promote(
    session: Session,
    email: Optional[str] = None,
    employee_code: Optional[str] = None,
    allow_additional_super_admin: bool = False,
    update_existing_permissions: bool = False,
    auto_confirm: bool = False,
    dry_run: bool = False,
    password_getter: Callable[[str], str] = getpass.getpass,
    input_getter: Callable[[str], str] = input,
) -> User:
    """Execute Mode 2: Promote an existing employee to Super Admin."""
    if not email and not employee_code:
        raise BootstrapError("Please provide either --email or --employee-code to locate the employee.")

    stmt = select(User)
    if email:
        email_clean = normalize_email_address(email, "official_email")
        stmt = stmt.where(func.lower(User.official_email) == email_clean)
    else:
        code_clean = employee_code.strip().upper()
        stmt = stmt.where(User.employee_code == code_clean)

    user = session.execute(stmt).scalar_one_or_none()
    if not user:
        identifier = email or employee_code
        raise BootstrapError(f"Employee with identifier '{identifier}' was not found in user_master.")

    if user.account_status != "ACTIVE":
        raise BootstrapError(
            f"Employee '{user.employee_code}' has account_status '{user.account_status}'. Only ACTIVE accounts can be promoted."
        )

    # Super Admin Safety Check (excluding this user if already super admin)
    existing_super_admins = [
        a for a in get_existing_super_admins(session) if a.user_id != user.user_id
    ]
    if existing_super_admins and not allow_additional_super_admin:
        admin_summaries = ", ".join(
            f"{a.employee_code} ({a.first_name} {a.last_name}, {a.official_email})"
            for a in existing_super_admins
        )
        raise BootstrapError(
            f"Another Super Admin account already exists: {admin_summaries}. "
            f"To promote an additional unrestricted Super Admin, pass --allow-additional-super-admin."
        )

    # Fetch active modules
    active_modules = session.execute(
        select(Module).where(Module.status == "ACTIVE").order_by(Module.display_order.asc())
    ).scalars().all()
    if not active_modules:
        raise BootstrapError("No active modules found in module_master. Run seed_modules first.")

    has_existing_password = bool(user.password_hash and user.password_hash.strip())

    # Display Safe Summary
    print("\n" + "=" * 72)
    print("GOCOMPLIANCE CRM - SUPER ADMIN BOOTSTRAP SUMMARY (PROMOTE MODE)")
    print("=" * 72)
    print(f"Operation Type     : PROMOTE EXISTING EMPLOYEE TO SUPER ADMIN")
    print(f"Employee Code      : {user.employee_code}")
    print(f"Employee Name      : {user.first_name} {user.last_name}")
    print(f"Official Email     : {user.official_email}")
    print(f"Account Status     : {user.account_status}")
    print(f"Password Status    : {'Unchanged (Already configured)' if has_existing_password else 'Initial password will be securely set'}")
    print(f"Assigned Data Scope: ALL (Unrestricted across all companies)")
    print(f"Action Rights      : VIEW, CREATE, EDIT, DELETE, APPROVE (Full)")
    print(f"Active Modules ({len(active_modules)}): {', '.join(m.module_code for m in active_modules)}")
    print("=" * 72)

    if dry_run:
        print("\n[DRY-RUN] Pre-flight validation successful. No database changes made.")
        return user

    # Password Handling
    new_password_hash: Optional[str] = None
    if not has_existing_password:
        print("\nEmployee does not currently have a password. Setting initial password...")
        pwd = prompt_for_password(password_getter=password_getter)
        new_password_hash = hash_password(pwd)
    else:
        print("\n[i] Note: Existing login password will remain untouched.")

    # Confirmation Prompt
    if not auto_confirm:
        print("\nType 'PROMOTE SUPER ADMIN' to proceed with granting elevated privileges:")
        conf = input_getter("Confirmation: ").strip()
        if conf != "PROMOTE SUPER ADMIN":
            raise BootstrapError("Operation aborted by user. Confirmation mismatch.")

    # Atomic Transaction
    try:
        if new_password_hash:
            user.password_hash = new_password_hash
            user.must_change_password = False

        grant_count = grant_all_module_permissions(
            session=session,
            user_id=user.user_id,
            update_existing_permissions=update_existing_permissions,
        )
        session.commit()
        session.refresh(user)

        print("\n" + "=" * 72)
        print("EMPLOYEE PROMOTED TO SUPER ADMIN SUCCESSFULLY")
        print("=" * 72)
        print(f"Employee Code : {user.employee_code}")
        print(f"Official Email: {user.official_email}")
        print(f"Name          : {user.first_name} {user.last_name}")
        print(f"Permissions   : {grant_count} active modules assigned with 'ALL' data scope.")
        print(f"Status        : ACTIVE (Ready to log in at http://localhost:8001)")
        print("=" * 72)
        return user

    except Exception as exc:
        session.rollback()
        raise BootstrapError(f"Database transaction failed during Super Admin promotion: {exc}")


def build_cli_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser for Super Admin bootstrap."""
    parser = argparse.ArgumentParser(
        prog="python -m app.scripts.bootstrap_super_admin",
        description="GOCOMPLIANCE CRM - Secure Super Admin Bootstrap CLI Utility",
    )
    subparsers = parser.add_subparsers(dest="command", help="Bootstrap mode")

    # Create Mode Subparser
    create_p = subparsers.add_parser(
        "create",
        help="Create and initialize a new Super Admin employee account",
    )
    create_p.add_argument("--email", required=True, help="Official corporate email address (unique)")
    create_p.add_argument("--first-name", required=True, help="Employee first name")
    create_p.add_argument("--last-name", required=True, help="Employee last name")
    create_p.add_argument("--middle-name", default=None, help="Employee middle name (optional)")
    create_p.add_argument("--phone", required=True, help="Primary contact mobile number (+91 or 10 digits)")
    create_p.add_argument("--company-code", required=True, help="Company code or prefix (e.g. GOCOMPLIANCES or CG)")
    create_p.add_argument("--department-code", required=True, help="Department code (e.g. ADMINISTRATION)")
    create_p.add_argument("--designation-code", required=True, help="Designation code (e.g. DIRECTOR)")
    create_p.add_argument(
        "--joining-date",
        type=lambda d: date.fromisoformat(d),
        default=None,
        help="Date of joining (YYYY-MM-DD, default: today)",
    )
    create_p.add_argument("--personal-email", default=None, help="Personal email address (optional)")
    create_p.add_argument(
        "--employment-type",
        default="FULL_TIME",
        choices=["FULL_TIME", "PART_TIME", "CONTRACT", "INTERN", "CONSULTANT"],
        help="Employment type (default: FULL_TIME)",
    )
    create_p.add_argument(
        "--allow-additional-super-admin",
        action="store_true",
        help="Allow creating an additional Super Admin if one already exists",
    )
    create_p.add_argument(
        "--update-existing-permissions",
        action="store_true",
        help="Explicitly update module permission rows if present",
    )
    create_p.add_argument(
        "--yes",
        "--non-interactive",
        dest="yes",
        action="store_true",
        help="Skip interactive confirmation prompt",
    )
    create_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform validations and display summary without changing database or prompting password",
    )

    # Promote Mode Subparser
    promote_p = subparsers.add_parser(
        "promote",
        help="Promote an existing employee account to Super Admin status",
    )
    promote_p.add_argument("--email", default=None, help="Official email of the existing employee")
    promote_p.add_argument("--employee-code", default=None, help="Employee code of the existing employee")
    promote_p.add_argument(
        "--allow-additional-super-admin",
        action="store_true",
        help="Allow promoting an additional Super Admin if one already exists",
    )
    promote_p.add_argument(
        "--update-existing-permissions",
        action="store_true",
        help="Explicitly update module permission rows if present",
    )
    promote_p.add_argument(
        "--yes",
        "--non-interactive",
        dest="yes",
        action="store_true",
        help="Skip interactive confirmation prompt",
    )
    promote_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform validations and display summary without changing database or prompting password",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Main CLI execution entrypoint."""
    parser = build_cli_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    with SessionLocal() as session:
        try:
            if args.command == "create":
                execute_bootstrap_create(
                    session=session,
                    email=args.email,
                    first_name=args.first_name,
                    last_name=args.last_name,
                    middle_name=args.middle_name,
                    phone=args.phone,
                    company_code=args.company_code,
                    department_code=args.department_code,
                    designation_code=args.designation_code,
                    joining_date=args.joining_date,
                    personal_email=args.personal_email,
                    employment_type=args.employment_type,
                    allow_additional_super_admin=args.allow_additional_super_admin,
                    update_existing_permissions=args.update_existing_permissions,
                    auto_confirm=args.yes,
                    dry_run=args.dry_run,
                )
            elif args.command == "promote":
                execute_bootstrap_promote(
                    session=session,
                    email=args.email,
                    employee_code=args.employee_code,
                    allow_additional_super_admin=args.allow_additional_super_admin,
                    update_existing_permissions=args.update_existing_permissions,
                    auto_confirm=args.yes,
                    dry_run=args.dry_run,
                )
        except BootstrapError as err:
            print(f"\n[-] ERROR: {err}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:
            print(f"\n[-] UNEXPECTED ERROR: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
