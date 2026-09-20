"""Safe cleanup CLI script for removing automated test data from development database.

Targets only records with:
- official_email ends with '@trialorg.com'
- company_name begins with 'Trial Org'
- dependent departments, designations, permissions, and tokens belonging exclusively to test entities.

Strictly protects legitimate records:
- CG0001 (Super Admin)
- CG0002 (Muskan Gupta)
- GOCOMPLIANCES, ENTERPERNERSHIP, BRANDMINGO

Usage:
    Dry-run (default, non-destructive):
        python -m app.scripts.cleanup_trial_test_data
        python -m app.scripts.cleanup_trial_test_data --dry-run

    Execute (interactive confirmation required):
        python -m app.scripts.cleanup_trial_test_data --execute
"""
import argparse
import logging
import sys
from typing import Dict, List, Set
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import SessionLocal, engine
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.models.user_module_permission import UserModulePermission

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("cleanup_trial_test_data")

PROTECTED_EMPLOYEE_CODES = {"CG0001", "CG0002"}
PROTECTED_COMPANY_CODES = {"GOCOMPLIANCES", "ENTERPERNERSHIP", "BRANDMINGO"}
CONFIRMATION_STRING = "DELETE TRIAL TEST DATA"


def get_safe_db_identifier() -> str:
    """Return masked database identifier for safe reporting."""
    try:
        url = make_url(settings.DATABASE_URL)
        return f"{url.host or 'localhost'}:{url.port or 5432}/{url.database}"
    except Exception:
        return "configured database"


def verify_environment_safety() -> None:
    """Verify that script is not running against a production database."""
    if settings.is_production:
        print("\n" + "=" * 70, file=sys.stderr)
        print("ERROR: Safety check failed! Production environment detected.", file=sys.stderr)
        print("This cleanup tool is strictly forbidden from running in production.", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        sys.exit(1)


def inspect_targets(session: Session) -> Dict[str, any]:
    """Inspect and collect candidate test records and verify isolation from legitimate records."""
    # 1. Test Companies
    test_companies = (
        session.query(Company)
        .filter(Company.company_name.like("Trial Org%"))
        .order_by(Company.company_name)
        .all()
    )
    test_company_ids: Set[UUID] = {c.company_id for c in test_companies}

    # 2. Test Users
    test_users = (
        session.query(User)
        .filter(User.official_email.like("%@trialorg.com"))
        .order_by(User.employee_code)
        .all()
    )
    test_user_ids: Set[UUID] = {u.user_id for u in test_users}

    # 3. Test Departments (belonging to test companies)
    test_departments = (
        session.query(Department)
        .filter(Department.company_id.in_(test_company_ids))
        .all()
        if test_company_ids
        else []
    )
    test_department_ids: Set[UUID] = {d.department_id for d in test_departments}

    # 4. Test Designations (belonging to test companies)
    test_designations = (
        session.query(Designation)
        .filter(Designation.company_id.in_(test_company_ids))
        .all()
        if test_company_ids
        else []
    )
    test_designation_ids: Set[UUID] = {d.designation_id for d in test_designations}

    # 5. Test UserModulePermissions
    test_permissions = (
        session.query(UserModulePermission)
        .filter(UserModulePermission.user_id.in_(test_user_ids))
        .all()
        if test_user_ids
        else []
    )

    # 6. Test RefreshTokens
    test_tokens = (
        session.query(RefreshToken)
        .filter(RefreshToken.user_id.in_(test_user_ids))
        .all()
        if test_user_ids
        else []
    )

    # 7. Legitimate Records
    legit_companies = (
        session.query(Company)
        .filter(~Company.company_name.like("Trial Org%"))
        .order_by(Company.company_code)
        .all()
    )
    legit_company_ids = {c.company_id for c in legit_companies}

    legit_users = (
        session.query(User)
        .filter(~User.official_email.like("%@trialorg.com"))
        .order_by(User.employee_code)
        .all()
    )
    legit_user_ids = {u.user_id for u in legit_users}

    # ================= SAFETY VALIDATIONS =================
    safety_violations = []

    # Check 1: Protected employee codes in deletion set
    for u in test_users:
        if u.employee_code in PROTECTED_EMPLOYEE_CODES:
            safety_violations.append(f"Protected employee code '{u.employee_code}' found in test deletion set!")

    # Check 2: Protected company codes in deletion set
    for c in test_companies:
        if c.company_code in PROTECTED_COMPANY_CODES:
            safety_violations.append(f"Protected company code '{c.company_code}' found in test deletion set!")

    # Check 3: Non-test users belonging to test companies
    if test_company_ids:
        non_test_users_in_test_comp = (
            session.query(User)
            .filter(
                User.company_id.in_(test_company_ids),
                ~User.official_email.like("%@trialorg.com"),
            )
            .all()
        )
        if non_test_users_in_test_comp:
            for u in non_test_users_in_test_comp:
                safety_violations.append(
                    f"Non-test user '{u.employee_code}' ({u.official_email}) belongs to test company '{u.company_id}'!"
                )

    # Check 4: Test users belonging to legitimate companies
    if legit_company_ids:
        test_users_in_legit_comp = (
            session.query(User)
            .filter(
                User.company_id.in_(legit_company_ids),
                User.official_email.like("%@trialorg.com"),
            )
            .all()
        )
        if test_users_in_legit_comp:
            for u in test_users_in_legit_comp:
                safety_violations.append(
                    f"Test user '{u.employee_code}' ({u.official_email}) is assigned to legitimate company '{u.company_id}'!"
                )

    # Check 5: Legitimate users managed by test users
    if test_user_ids and legit_user_ids:
        legit_managed_by_test = (
            session.query(User)
            .filter(
                User.user_id.in_(legit_user_ids),
                User.manager_user_id.in_(test_user_ids),
            )
            .all()
        )
        if legit_managed_by_test:
            for u in legit_managed_by_test:
                safety_violations.append(
                    f"Legitimate user '{u.employee_code}' has reporting manager pointing to test user '{u.manager_user_id}'!"
                )

    if safety_violations:
        print("\n" + "=" * 70, file=sys.stderr)
        print("CRITICAL SAFETY VIOLATION DETECTED! Aborting.", file=sys.stderr)
        for v in safety_violations:
            print(f"  - {v}", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        sys.exit(1)

    return {
        "test_companies": test_companies,
        "test_company_ids": test_company_ids,
        "test_users": test_users,
        "test_user_ids": test_user_ids,
        "test_departments": test_departments,
        "test_department_ids": test_department_ids,
        "test_designations": test_designations,
        "test_designation_ids": test_designation_ids,
        "test_permissions_count": len(test_permissions),
        "test_tokens_count": len(test_tokens),
        "legit_companies": legit_companies,
        "legit_users": legit_users,
    }


def print_preview(data: Dict[str, any], is_dry_run: bool = True) -> None:
    """Display structured summary table of records targeted for removal and excluded legitimate records."""
    mode_str = "DRY-RUN PREVIEW" if is_dry_run else "TARGET DELETION SUMMARY"
    print("\n" + "=" * 75)
    print(f"  GOCOMPLIANCE CRM - TRIAL TEST DATA CLEANUP TOOL ({mode_str})")
    print("=" * 75)
    print(f"Target Database : {get_safe_db_identifier()}")
    print(f"Environment     : {settings.ENVIRONMENT} (APP_ENV={settings.APP_ENV or 'not set'})")
    print("-" * 75)

    print("\n[AFFECTED RECORDS IDENTIFIED FOR REMOVAL]")
    print(f"  • Test Companies (company_name LIKE 'Trial Org%')       : {len(data['test_companies']):>4}")
    print(f"  • Test Departments (belonging to test companies)        : {len(data['test_departments']):>4}")
    print(f"  • Test Designations (belonging to test companies)       : {len(data['test_designations']):>4}")
    print(f"  • Test Employees (official_email LIKE '%@trialorg.com') : {len(data['test_users']):>4}")
    print(f"  • Test User Permissions (user_module_permission)       : {data['test_permissions_count']:>4}")
    print(f"  • Test Refresh Tokens (auth_refresh_token)              : {data['test_tokens_count']:>4}")
    total_records = (
        len(data["test_companies"])
        + len(data["test_departments"])
        + len(data["test_designations"])
        + len(data["test_users"])
        + data["test_permissions_count"]
        + data["test_tokens_count"]
    )
    print(f"  TOTAL CANDIDATE RECORDS TO CLEAN                        : {total_records:>4}")

    if data["test_companies"]:
        print(f"\n[SAMPLE TEST COMPANIES TO REMOVE (showing up to 10 of {len(data['test_companies'])})]")
        for c in data["test_companies"][:10]:
            print(f"  - [{c.company_code:<6}] {c.company_name:<25} (Prefix: {c.employee_code_prefix})")
        if len(data["test_companies"]) > 10:
            print(f"    ... and {len(data['test_companies']) - 10} more test companies")

    print("\n[CONFIRMED PROTECTED LEGITIMATE RECORDS (WILL NOT BE MODIFIED)]")
    print("  Legitimate Companies:")
    for c in data["legit_companies"]:
        print(f"    ✓ [{c.company_code:<16}] {c.company_name:<20} (Prefix: {c.employee_code_prefix})")

    print("  Legitimate Employees:")
    for u in data["legit_users"]:
        print(f"    ✓ [{u.employee_code:<8}] {u.first_name} {u.last_name:<18} ({u.official_email})")

    print("=" * 75)


def execute_deletion(session: Session, data: Dict[str, any]) -> None:
    """Execute foreign-key-safe atomic deletion inside a single transaction."""
    test_user_ids = list(data["test_user_ids"])
    test_company_ids = list(data["test_company_ids"])

    if not test_user_ids and not test_company_ids:
        print("\nNo trial test records found to delete. Database is already clean.")
        return

    print("\nInitiating atomic deletion transaction...")

    try:
        # Step 1: Break self-referencing reporting manager FKs on test users
        if test_user_ids:
            updated_mgrs = (
                session.query(User)
                .filter(User.user_id.in_(test_user_ids), User.manager_user_id.isnot(None))
                .update({User.manager_user_id: None}, synchronize_session=False)
            )
            logger.info("Step 1/7: Cleared manager_user_id self-references (%d updated)", updated_mgrs)

        # Step 2: Delete test user module permissions
        if test_user_ids:
            deleted_perms = (
                session.query(UserModulePermission)
                .filter(UserModulePermission.user_id.in_(test_user_ids))
                .delete(synchronize_session=False)
            )
            logger.info("Step 2/7: Deleted user_module_permission records (%d deleted)", deleted_perms)

        # Step 3: Delete test user refresh tokens
        if test_user_ids:
            deleted_tokens = (
                session.query(RefreshToken)
                .filter(RefreshToken.user_id.in_(test_user_ids))
                .delete(synchronize_session=False)
            )
            logger.info("Step 3/7: Deleted auth_refresh_token records (%d deleted)", deleted_tokens)

        # Step 4: Delete test users
        if test_user_ids:
            deleted_users = (
                session.query(User)
                .filter(User.user_id.in_(test_user_ids))
                .delete(synchronize_session=False)
            )
            logger.info("Step 4/7: Deleted user_master records (%d deleted)", deleted_users)

        # Step 5: Delete test designations
        if test_company_ids:
            deleted_desigs = (
                session.query(Designation)
                .filter(Designation.company_id.in_(test_company_ids))
                .delete(synchronize_session=False)
            )
            logger.info("Step 5/7: Deleted designation_master records (%d deleted)", deleted_desigs)

        # Step 6: Delete test departments
        if test_company_ids:
            deleted_depts = (
                session.query(Department)
                .filter(Department.company_id.in_(test_company_ids))
                .delete(synchronize_session=False)
            )
            logger.info("Step 6/7: Deleted department_master records (%d deleted)", deleted_depts)

        # Step 7: Delete test companies
        if test_company_ids:
            deleted_comps = (
                session.query(Company)
                .filter(Company.company_id.in_(test_company_ids))
                .delete(synchronize_session=False)
            )
            logger.info("Step 7/7: Deleted company_master records (%d deleted)", deleted_comps)

        # Verification step inside transaction before committing
        remaining_test_users = session.query(User).filter(User.official_email.like("%@trialorg.com")).count()
        remaining_test_comps = session.query(Company).filter(Company.company_name.like("Trial Org%")).count()

        if remaining_test_users > 0 or remaining_test_comps > 0:
            raise RuntimeError(
                f"Post-delete verification failed: {remaining_test_users} users and {remaining_test_comps} companies remain!"
            )

        # Verify all protected legitimate records remain intact
        for code in PROTECTED_EMPLOYEE_CODES:
            u_check = session.query(User).filter(User.employee_code == code).first()
            if not u_check:
                raise RuntimeError(f"Post-delete verification failed: Protected employee '{code}' is missing!")

        for c_code in PROTECTED_COMPANY_CODES:
            c_check = session.query(Company).filter(Company.company_code == c_code).first()
            if not c_check:
                raise RuntimeError(f"Post-delete verification failed: Protected company '{c_code}' is missing!")

        # Commit transaction
        session.commit()
        print("\n" + "=" * 75)
        print("SUCCESS: Trial test data cleanup successfully executed and committed.")
        print(f"  • user_master rows deleted            : {deleted_users}")
        print(f"  • company_master rows deleted         : {deleted_comps}")
        print(f"  • department_master rows deleted      : {deleted_depts}")
        print(f"  • designation_master rows deleted     : {deleted_desigs}")
        print(f"  • user_module_permission rows deleted : {deleted_perms}")
        print(f"  • auth_refresh_token rows deleted     : {deleted_tokens}")
        print("\nPost-cleanup database verification:")
        print("  ✓ Users with @trialorg.com  : 0")
        print("  ✓ Companies with Trial Org  : 0")
        print("  ✓ Legitimate records intact : CG0001, CG0002, GOCOMPLIANCES, ENTERPERNERSHIP, BRANDMINGO")
        print("=" * 75 + "\n")

    except Exception as e:
        session.rollback()
        logger.error("Deletion transaction failed and was rolled back: %s", str(e), exc_info=True)
        print("\n" + "=" * 75, file=sys.stderr)
        print("ERROR: Cleanup transaction failed. All changes have been rolled back.", file=sys.stderr)
        print(f"Reason: {str(e)}", file=sys.stderr)
        print("=" * 75 + "\n", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Safe cleanup tool for automated test data in GOCOMPLIANCE CRM."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview test records targeted for removal without making database changes (default).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the deletion inside an atomic transaction (requires confirmation).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip interactive confirmation prompt when --execute is specified.",
    )

    args = parser.parse_args()

    # If --execute is specified, turn off dry-run mode
    is_dry_run = not args.execute

    verify_environment_safety()

    session: Session = SessionLocal()
    try:
        data = inspect_targets(session)
        print_preview(data, is_dry_run=is_dry_run)

        if is_dry_run:
            print("\n[DRY-RUN] NO DATA WAS DELETED. Database was NOT modified.")
            print("To execute deletion, run with --execute after manual review:")
            print("    python -m app.scripts.cleanup_trial_test_data --execute\n")
            return

        # Execution Confirmation
        if not args.force:
            print("\nWARNING: You are about to permanently delete the candidate test records listed above.")
            print(f"To proceed, please type exactly '{CONFIRMATION_STRING}': ")
            user_input = input("> ").strip()
            if user_input != CONFIRMATION_STRING:
                print("\nConfirmation mismatch. Operation aborted. No data was deleted.\n")
                return

        execute_deletion(session, data)

    finally:
        session.close()


if __name__ == "__main__":
    main()
