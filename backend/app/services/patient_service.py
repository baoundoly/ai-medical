from datetime import datetime

from sqlalchemy.orm import Session

from app.models.patient import Patient


def generate_patient_uid(db: Session, tenant_code: str, city_code: str) -> str:
    """
    Generate a unique patient UID in the format:
    {TENANT_CODE}-{CITY}-{YEAR}-{6-digit-sequence}
    e.g. HSP-DHK-2026-000001
    """
    year = datetime.utcnow().year
    prefix = f"{tenant_code.upper()}-{city_code.upper()}-{year}"

    # Count existing patients with this year's prefix to get next sequence
    count = (
        db.query(Patient)
        .filter(Patient.patient_uid.like(f"{prefix}-%"))
        .count()
    )
    sequence = count + 1
    return f"{prefix}-{sequence:06d}"


def check_duplicate_patients(
    db: Session,
    tenant_id: int,
    name: str,
    mobile: str = None,
    dob=None,
) -> list[Patient]:
    """
    Check for potential duplicate patients by name, mobile, or date-of-birth.
    Returns a list of likely duplicates.
    """
    query = db.query(Patient).filter(
        Patient.tenant_id == tenant_id,
        Patient.is_active == True,
    )

    candidates = []

    # Exact mobile match is a strong signal
    if mobile:
        by_mobile = query.filter(Patient.mobile == mobile).all()
        candidates.extend(by_mobile)

    # Name + DOB combination
    if dob:
        by_name_dob = (
            query.filter(Patient.name.ilike(f"%{name}%"), Patient.dob == dob).all()
        )
        candidates.extend(by_name_dob)
    else:
        # Fuzzy name-only match (simple contains)
        by_name = query.filter(Patient.name.ilike(f"%{name}%")).all()
        candidates.extend(by_name)

    # Deduplicate by patient id
    seen = set()
    unique = []
    for p in candidates:
        if p.id not in seen:
            seen.add(p.id)
            unique.append(p)
    return unique
