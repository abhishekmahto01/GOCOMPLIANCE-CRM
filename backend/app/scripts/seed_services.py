"""Seed initial Service Master catalog and document checklist configurations."""
import uuid
from decimal import Decimal
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.service import ServiceMaster, ServiceRequiredDocument

SERVICE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "gocompliance.crm.services")


def get_deterministic_service_uuid(service_code: str) -> uuid.UUID:
    """Generate a deterministic UUIDv5 for service code."""
    return uuid.uuid5(SERVICE_NAMESPACE, service_code.upper())


INITIAL_SERVICES: List[Dict[str, object]] = [
    {
        "service_code": "TRADE_LICENSE",
        "service_name": "Trade License",
        "category": "LICENCE",
        "description": "Municipal corporation business trade license and renewal",
        "base_price": Decimal("15000.00"),
        "govt_fee": Decimal("2500.00"),
        "standard_turnaround_days": 15,
        "docs": [
            {"code": "PAN", "name": "PAN Card of Entity/Proprietor", "mandatory": True, "order": 10},
            {"code": "AADHAAR", "name": "Aadhaar Card of Applicant", "mandatory": True, "order": 20},
            {"code": "RENT_AGREEMENT", "name": "Registered Rent Agreement / NOC", "mandatory": True, "order": 30},
            {"code": "PROPERTY_TAX", "name": "Property Tax Receipt", "mandatory": True, "order": 40},
            {"code": "ELECTRICITY_BILL", "name": "Recent Electricity Bill", "mandatory": True, "order": 50},
        ],
    },
    {
        "service_code": "SHOP_ACT",
        "service_name": "Shop Act",
        "category": "REGISTRATION",
        "description": "State shops and commercial establishments registration (Gumasta)",
        "base_price": Decimal("8000.00"),
        "govt_fee": Decimal("1200.00"),
        "standard_turnaround_days": 7,
        "docs": [
            {"code": "PAN", "name": "PAN Card of Business Owner", "mandatory": True, "order": 10},
            {"code": "AADHAAR", "name": "Aadhaar Card of Authorized Person", "mandatory": True, "order": 20},
            {"code": "GEO_IMAGE", "name": "Geo-tagged photo of shop with signboard", "mandatory": True, "order": 30},
            {"code": "RENT_AGREEMENT", "name": "Rent Agreement / Ownership Proof", "mandatory": True, "order": 40},
        ],
    },
    {
        "service_code": "CLRA",
        "service_name": "CLRA Registration",
        "category": "COMPLIANCE",
        "description": "Contract Labour Regulation and Abolition statutory licence",
        "base_price": Decimal("25000.00"),
        "govt_fee": Decimal("5000.00"),
        "standard_turnaround_days": 21,
        "docs": [
            {"code": "COI", "name": "Certificate of Incorporation", "mandatory": True, "order": 10},
            {"code": "FORM_V", "name": "Form V issued by Principal Employer", "mandatory": True, "order": 20},
            {"code": "PAN", "name": "Company PAN Card", "mandatory": True, "order": 30},
            {"code": "AGREEMENT", "name": "Master Services Agreement with Principal Employer", "mandatory": True, "order": 40},
        ],
    },
    {
        "service_code": "PCB",
        "service_name": "PCB Consent",
        "category": "LICENCE",
        "description": "Pollution Control Board Consent to Establish and Operate (CTE/CTO)",
        "base_price": Decimal("40000.00"),
        "govt_fee": Decimal("15000.00"),
        "standard_turnaround_days": 30,
        "docs": [
            {"code": "SITE_PLAN", "name": "Site Layout and Plant Machinery Plan", "mandatory": True, "order": 10},
            {"code": "PROJECT_REPORT", "name": "Detailed Project Report on Emissions/Effluents", "mandatory": True, "order": 20},
            {"code": "LAND_DOCS", "name": "Land Possession / Ownership Documents", "mandatory": True, "order": 30},
            {"code": "COI", "name": "Certificate of Incorporation / Registration", "mandatory": True, "order": 40},
            {"code": "WATER_NOC", "name": "Water Connection NOC / Supply Bill", "mandatory": False, "order": 50},
        ],
    },
    {
        "service_code": "CLINICAL_ESTABLISHMENT",
        "service_name": "Clinical Establishment",
        "category": "LICENCE",
        "description": "Clinical Establishment Act registration for clinics, hospitals, and diagnostic labs",
        "base_price": Decimal("35000.00"),
        "govt_fee": Decimal("10000.00"),
        "standard_turnaround_days": 25,
        "docs": [
            {"code": "DOCTOR_DEGREE", "name": "Medical Council Registration & Degrees of Doctors", "mandatory": True, "order": 10},
            {"code": "STAFF_DETAILS", "name": "Nursing and Paramedical Staff Credentials", "mandatory": True, "order": 20},
            {"code": "FIRE_NOC", "name": "Fire Department Safety NOC", "mandatory": True, "order": 30},
            {"code": "BM_WASTE", "name": "Bio-Medical Waste Management Agreement", "mandatory": True, "order": 40},
        ],
    },
    {
        "service_code": "PESO",
        "service_name": "PESO",
        "category": "LICENCE",
        "description": "Petroleum and Explosives Safety Organisation statutory approvals",
        "base_price": Decimal("60000.00"),
        "govt_fee": Decimal("25000.00"),
        "standard_turnaround_days": 45,
        "docs": [
            {"code": "EXPLOSIVE_PLAN", "name": "Approved Storage and Handling Blueprint", "mandatory": True, "order": 10},
            {"code": "SAFETY_CERT", "name": "Competent Person Safety & Fabricator Certificate", "mandatory": True, "order": 20},
            {"code": "DM_NOC", "name": "District Magistrate No Objection Certificate", "mandatory": True, "order": 30},
            {"code": "COI", "name": "Corporate Entity Incorporation Proof", "mandatory": True, "order": 40},
        ],
    },
    {
        "service_code": "PVT_LTD",
        "service_name": "Private Limited",
        "category": "INCORPORATION",
        "description": "Private Limited Company incorporation with MCA (SPICe+)",
        "base_price": Decimal("12000.00"),
        "govt_fee": Decimal("3000.00"),
        "standard_turnaround_days": 10,
        "docs": [
            {"code": "PAN_DIRECTORS", "name": "PAN Cards of all Proposed Directors", "mandatory": True, "order": 10},
            {"code": "ID_ADDRESS", "name": "Aadhaar / Passport and Bank Statement (Address Proof)", "mandatory": True, "order": 20},
            {"code": "OFFICE_PROOF", "name": "Electricity Bill and NOC from Property Owner", "mandatory": True, "order": 30},
            {"code": "DSC", "name": "Class 3 Digital Signature Certificate", "mandatory": True, "order": 40},
        ],
    },
    {
        "service_code": "LLP",
        "service_name": "LLP",
        "category": "INCORPORATION",
        "description": "Limited Liability Partnership registration with MCA (FiLLiP)",
        "base_price": Decimal("10000.00"),
        "govt_fee": Decimal("2000.00"),
        "standard_turnaround_days": 10,
        "docs": [
            {"code": "PAN_PARTNERS", "name": "PAN Cards of Designated Partners", "mandatory": True, "order": 10},
            {"code": "ID_PROOF", "name": "Identity & Address Proofs of Partners", "mandatory": True, "order": 20},
            {"code": "OFFICE_PROOF", "name": "Registered Office Address Proof & NOC", "mandatory": True, "order": 30},
            {"code": "LLP_AGREEMENT", "name": "Executed LLP Agreement", "mandatory": True, "order": 40},
        ],
    },
    {
        "service_code": "OPC",
        "service_name": "One Person Company",
        "category": "INCORPORATION",
        "description": "One Person Company incorporation with single shareholder & nominee",
        "base_price": Decimal("11000.00"),
        "govt_fee": Decimal("2500.00"),
        "standard_turnaround_days": 10,
        "docs": [
            {"code": "PAN_MEMBER", "name": "PAN Card of Member and Nominee", "mandatory": True, "order": 10},
            {"code": "NOMINEE_CONSENT", "name": "Form INC-3 Nominee Consent Letter", "mandatory": True, "order": 20},
            {"code": "OFFICE_PROOF", "name": "Registered Office Utility Bill & NOC", "mandatory": True, "order": 30},
        ],
    },
    {
        "service_code": "PARTNERSHIP",
        "service_name": "Partnership",
        "category": "REGISTRATION",
        "description": "Partnership Firm Deed Drafting and Registrar of Firms (ROF) Registration",
        "base_price": Decimal("7500.00"),
        "govt_fee": Decimal("1500.00"),
        "standard_turnaround_days": 12,
        "docs": [
            {"code": "DEED", "name": "Notarized Partnership Deed", "mandatory": True, "order": 10},
            {"code": "PAN_PARTNERS", "name": "PAN & Aadhaar of all Partners", "mandatory": True, "order": 20},
            {"code": "ADDRESS_PROOF", "name": "Principal Place of Business Proof", "mandatory": True, "order": 30},
        ],
    },
    {
        "service_code": "PROPRIETORSHIP",
        "service_name": "Proprietorship",
        "category": "REGISTRATION",
        "description": "Sole Proprietorship registration and banking compliance kit",
        "base_price": Decimal("5000.00"),
        "govt_fee": Decimal("500.00"),
        "standard_turnaround_days": 5,
        "docs": [
            {"code": "PAN", "name": "PAN Card of Proprietor", "mandatory": True, "order": 10},
            {"code": "AADHAAR", "name": "Aadhaar Card of Proprietor", "mandatory": True, "order": 20},
            {"code": "OFFICE_PROOF", "name": "Business Address Proof (Electricity / Rent Agreement)", "mandatory": True, "order": 30},
        ],
    },
]


def seed_services(session: Session) -> Tuple[int, int]:
    """Idempotently seed standard statutory services and document requirements.

    Args:
        session: Active SQLAlchemy database session.

    Returns:
        Tuple of (services_inserted, services_skipped).
    """
    inserted = 0
    skipped = 0

    existing_codes = set(session.scalars(select(ServiceMaster.service_code)).all())

    for s_data in INITIAL_SERVICES:
        code = str(s_data["service_code"])
        s_id = get_deterministic_service_uuid(code)

        if code in existing_codes:
            skipped += 1
            # Check if docs are present
            s_obj = session.get(ServiceMaster, s_id)
            if s_obj:
                existing_doc_codes = {d.document_code for d in s_obj.required_documents}
                for doc in s_data.get("docs", []):
                    if doc["code"] not in existing_doc_codes:
                        new_doc = ServiceRequiredDocument(
                            service_id=s_id,
                            document_code=doc["code"],
                            document_name=doc["name"],
                            is_mandatory=bool(doc.get("mandatory", True)),
                            display_order=int(doc.get("order", 0)),
                        )
                        session.add(new_doc)
            continue

        new_service = ServiceMaster(
            service_id=s_id,
            service_code=code,
            service_name=str(s_data["service_name"]),
            category=str(s_data["category"]),
            description=str(s_data.get("description", "")),
            base_price=Decimal(str(s_data.get("base_price", "0.00"))),
            govt_fee=Decimal(str(s_data.get("govt_fee", "0.00"))),
            standard_turnaround_days=int(s_data.get("standard_turnaround_days", 15)),
            status="ACTIVE",
        )
        session.add(new_service)
        session.flush()

        for doc in s_data.get("docs", []):
            new_doc = ServiceRequiredDocument(
                service_id=s_id,
                document_code=doc["code"],
                document_name=doc["name"],
                is_mandatory=bool(doc.get("mandatory", True)),
                display_order=int(doc.get("order", 0)),
            )
            session.add(new_doc)

        existing_codes.add(code)
        inserted += 1

    session.commit()
    return inserted, skipped


def main() -> None:
    """Run seed script directly from CLI."""
    session = SessionLocal()
    try:
        print("Starting Service Master seeding...")
        inserted, skipped = seed_services(session)
        print(f"Service seeding complete: {inserted} inserted, {skipped} skipped.")
    except Exception as exc:
        session.rollback()
        print(f"Error seeding services: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
