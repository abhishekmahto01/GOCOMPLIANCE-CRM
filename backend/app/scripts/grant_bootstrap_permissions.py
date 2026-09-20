"""One-time administrative bootstrap utility to grant initial permissions to a designated employee.

IMPORTANT:
- This script is an administrative CLI utility to be executed ONLY after a real Admin/Director user exists.
- DO NOT run this script during automated build/migrations or stage testing.
- This script does NOT create users or expose secrets.
"""
import argparse
import sys
from typing import List

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.module import Module
from app.models.user import User
from app.services.permissions import grant_or_update_permission


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap initial administrative permissions for a verified employee."
    )
    parser.add_argument(
        "--employee-code",
        type=str,
        required=True,
        help="Globally unique employee code (e.g. CG0001, EP0001, BM0001)",
    )
    parser.add_argument(
        "--scope",
        type=str,
        default="ALL",
        choices=["SELF", "TEAM", "DEPARTMENT", "COMPANY", "ALL"],
        help="Initial data scope (default: ALL)",
    )
    parser.add_argument(
        "--allow-delete",
        action="store_true",
        default=False,
        help="Explicitly enable can_delete (default is false for safety)",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        default=False,
        help="Bypass interactive confirmation prompt",
    )
    return parser.parse_args()


def grant_bootstrap_permissions(
    employee_code: str,
    scope: str = "ALL",
    allow_delete: bool = False,
    auto_confirm: bool = False,
) -> None:
    print("=" * 70)
    print("GOCOMPLIANCE-CRM: Administrative Permission Bootstrap Utility")
    print("WARNING: This utility assigns elevated administrative privileges.")
    print("=" * 70)

    code_clean = employee_code.strip().upper()

    with SessionLocal() as db:
        user = db.execute(
            select(User).where(User.employee_code == code_clean)
        ).scalar_one_or_none()

        if not user:
            print(f"[-] ERROR: Employee with code '{code_clean}' does not exist in user_master.", file=sys.stderr)
            sys.exit(1)

        if user.account_status != "ACTIVE":
            print(
                f"[-] ERROR: User '{code_clean}' account status is '{user.account_status}'. Must be 'ACTIVE'.",
                file=sys.stderr,
            )
            sys.exit(1)

        active_modules: List[Module] = db.execute(
            select(Module).where(Module.status == "ACTIVE").order_by(Module.display_order.asc())
        ).scalars().all()

        if not active_modules:
            print("[-] ERROR: No active modules found in module_master. Run seed_modules first.", file=sys.stderr)
            sys.exit(1)

        print(f"\nTarget Employee: {user.first_name} {user.last_name} ({user.official_email})")
        print(f"Employee Code  : {user.employee_code}")
        print(f"Target Scope   : {scope}")
        print(f"Actions Granted: view=True, create=True, edit=True, approve=True, delete={allow_delete}")
        print(f"Modules ({len(active_modules)}): {', '.join(m.module_code for m in active_modules)}")

        if not auto_confirm:
            confirmation = input("\nType 'CONFIRM' to execute bootstrap permission grant: ").strip()
            if confirmation != "CONFIRM":
                print("[-] Operation aborted by user.")
                sys.exit(0)

        print("\n[+] Granting module permissions...")
        granted_count = 0
        try:
            for mod in active_modules:
                grant_or_update_permission(
                    session=db,
                    user_id=user.user_id,
                    module_id=mod.module_id,
                    can_view=True,
                    can_create=True,
                    can_edit=True,
                    can_delete=allow_delete,
                    can_approve=True,
                    data_scope=scope,
                    status="ACTIVE",
                    is_bootstrap=True,
                )
                granted_count += 1
            db.commit()
            print(f"[+] SUCCESS: Successfully granted permissions on {granted_count} modules to {user.employee_code}.")
        except Exception as exc:
            db.rollback()
            print(f"[-] ERROR: Transaction failed: {exc}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    args = parse_args()
    grant_bootstrap_permissions(
        employee_code=args.employee_code,
        scope=args.scope,
        allow_delete=args.allow_delete,
        auto_confirm=args.confirm,
    )


if __name__ == "__main__":
    main()
