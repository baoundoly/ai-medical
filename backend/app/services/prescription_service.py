from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import generate_digital_signature
from app.models.prescription import DrugInteractionAlert, Prescription, PrescriptionItem
from app.services.ai_service import check_drug_interactions


def create_prescription(
    db: Session,
    visit_id: int,
    patient_id: int,
    doctor_id: int,
    items_data: list[dict],
) -> Prescription:
    """Create prescription with items and run drug interaction checks."""
    prescription = Prescription(
        visit_id=visit_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        status="draft",
        created_at=datetime.utcnow(),
    )
    db.add(prescription)
    db.flush()  # Get prescription.id before adding items

    for item_data in items_data:
        item = PrescriptionItem(prescription_id=prescription.id, **item_data)
        db.add(item)

    # Auto-detect drug interactions
    drug_names = [i.get("medicine_name", "") for i in items_data]
    interactions = check_drug_interactions(drug_names)
    for interaction in interactions:
        alert = DrugInteractionAlert(
            prescription_id=prescription.id,
            drug1=interaction["drug1"],
            drug2=interaction["drug2"],
            severity=interaction["severity"],
            message=interaction["message"],
        )
        db.add(alert)

    db.commit()
    db.refresh(prescription)
    return prescription


def sign_prescription(
    db: Session,
    prescription: Prescription,
    doctor_id: int,
    signature_method: str,
) -> Prescription:
    """Sign a prescription, generating a digital signature hash."""
    timestamp = datetime.utcnow().isoformat()
    signature_hash = generate_digital_signature(
        prescription.id, doctor_id, timestamp
    )
    prescription.digital_signature_hash = signature_hash
    prescription.signature_method = signature_method
    prescription.signed_at = datetime.utcnow()
    prescription.status = "approved"
    db.commit()
    db.refresh(prescription)
    return prescription


def validate_allergies(patient_allergies: list[str], drug_names: list[str]) -> list[str]:
    """
    Return list of allergen warnings for drugs the patient is allergic to.
    Simple substring match.
    """
    warnings = []
    for allergen in patient_allergies:
        for drug in drug_names:
            if allergen.lower() in drug.lower() or drug.lower() in allergen.lower():
                warnings.append(
                    f"Patient has documented allergy to '{allergen}' — matches '{drug}'"
                )
    return warnings
