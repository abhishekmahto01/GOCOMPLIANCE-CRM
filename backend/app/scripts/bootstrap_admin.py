"""Interactive CLI script to bootstrap the first Director / Admin employee.

IMPORTANT NOTE:
This utility must only be executed manually by an authorized administrator when approved
real Director details are provided. It must NOT be run automatically during migrations or tests.
"""
import getpass
import sys
from datetime import date
from typing import Optional

from sqlalchemy import func, select

from app.core.security import hash_password, validate_password_strength
from app.database.session import SessionLocal
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import create_user


def bootstrap_admin() -> None:
    """Prompt for real Director details, validate inputs, create user, and set initial password."""
    print("=" * 70)
    print("GOCOMPLIANCE CRM - First Director / Admin Account Bootstrap")
    print("=" * 70)
    print("This utility creates the first root administrator in the system.")
    print("All inputs must correspond to approved, real corporate details.\n")

    session = SessionLocal()
    try:
        # 1. Company selection
        company_code = input("Enter Company Code (e.g., GOCOMPLIANCES): ").strip().upper()
        company = session.execute(
            select(Company).where(Company.company_code == company_code)
        ).scalar_one_or_none()

        if not company:
            print(f"Error: Company '{company_code}' does not exist.")
            sys.exit(1)

        # 2. Department selection
        dept_code = input("Enter Department Code (e.g., ADMINISTRATION): ").strip().upper()
        department = session.execute(
            select(Department).where(
                Department.company_id == company.company_id,
                Department.department_code == dept_code,
            )
        ).scalar_one_or_none()

        if not department:
            print(f"Error: Department '{dept_code}' not found for company '{company_code}'.")
            sys.exit(1)

        # 3. Designation selection
        desig_code = input("Enter Designation Code (e.g., DIRECTOR): ").strip().upper()
        designation = session.execute(
            select(Designation).where(
                Designation.company_id == company.company_id,
                Designation.designation_code == desig_code,
            )
        ).scalar_one_or_none()

        if not designation:
            print(f"Error: Designation '{desig_code}' not found for company '{company_code}'.")
            sys.exit(1)

        # 4. Personal Information
        first_name = input("First Name: ").strip()
        middle_name_raw = input("Middle Name (optional, press Enter to skip): ").strip()
        middle_name: Optional[str] = middle_name_raw if middle_name_raw else None
        last_name = input("Last Name: ").strip()
        official_email = input("Official Email: ").strip().lower()
        personal_email_raw = input("Personal Email (optional, press Enter to skip): ").strip().lower()
        personal_email: Optional[str] = personal_email_raw if personal_email_raw else None
        mobile_number = input("Mobile Number (+91 format or 10 digits): ").strip()
        joining_date_str = input("Date of Joining (YYYY-MM-DD): ").strip()

        try:
            joining_date = date.fromisoformat(joining_date_str)
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")
            sys.exit(1)

        # 5. Check duplicate email
        existing_user = session.execute(
            select(User).where(func.lower(User.official_email) == official_email)
        ).scalar_one_or_none()

        if existing_user:
            print(f"Error: Official email '{official_email}' is already registered.")
            sys.exit(1)

        # 6. Password Input (Hidden)
        print("\nEnter initial password for the Director account:")
        password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm Password: ")

        if password != confirm_password:
            print("Error: Passwords do not match.")
            sys.exit(1)

        try:
            validate_password_strength(password)
        except ValueError as err:
            print(f"Error in password complexity: {err}")
            sys.exit(1)

        # 7. Create User with atomic code assignment
        user_in = UserCreate(
            company_id=company.company_id,
            department_id=department.department_id,
            designation_id=designation.designation_id,
            manager_user_id=None,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            official_email=official_email,
            personal_email=personal_email,
            mobile_number=mobile_number,
            date_of_joining=joining_date,
            employment_type="FULL_TIME",
            account_status="ACTIVE",
        )

        user = create_user(session=session, user_in=user_in)

        # Set initial password hash and must_change_password flag
        user.password_hash = hash_password(password)
        user.must_change_password = True
        session.commit()

        print("\n" + "=" * 70)
        print("Director Account Successfully Created!")
        print(f"Employee Code:  {user.employee_code}")
        print(f"Name:           {user.first_name} {user.last_name}")
        print(f"Official Email: {user.official_email}")
        print(f"Company:        {company.company_name}")
        print(f"Department:     {department.department_name}")
        print(f"Designation:    {designation.designation_name}")
        print("=" * 70)

    except Exception as err:
        session.rollback()
        print(f"\nAn error occurred during account creation: {err}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    bootstrap_admin()
