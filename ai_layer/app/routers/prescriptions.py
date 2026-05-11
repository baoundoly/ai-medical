from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.patient import PatientAllergy
from app.models.prescription import DrugInteractionAlert, Prescription
from app.models.user import Role, User
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionResponse,
    PrescriptionSignRequest,
    VoicePrescriptionRequest,
)
from app.services import audit_service, prescription_service
from app.services.ai_service import parse_voice_prescription

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.post("/", response_model=PrescriptionResponse, status_code=201)
def create_prescription(
    payload: PrescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.doctor, Role.super_admin])
    items = [item.model_dump() for item in payload.items]
    presc = prescription_service.create_prescription(
        db, payload.visit_id, payload.patient_id, payload.doctor_id, items
    )
    # Check patient allergies against prescribed drugs
    allergies = db.query(PatientAllergy).filter(PatientAllergy.patient_id == payload.patient_id).all()
    allergen_names = [a.allergen for a in allergies]
    drug_names = [i.get("medicine_name", "") for i in items]
    warnings = prescription_service.validate_allergies(allergen_names, drug_names)
    audit_service.log_action(
        db, current_user.id, "create", "prescription", presc.id, current_user.tenant_id,
        details=f"allergy_warnings={warnings}",
    )
    return presc


@router.post("/{presc_id}/sign", response_model=PrescriptionResponse)
def sign_prescription(
    presc_id: int,
    payload: PrescriptionSignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.doctor, Role.super_admin])
    presc = db.query(Prescription).filter(Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    if presc.doctor_id != current_user.id and current_user.role != Role.super_admin:
        raise HTTPException(status_code=403, detail="Only the prescribing doctor can sign")
    if presc.status == "approved":
        raise HTTPException(status_code=400, detail="Prescription already signed")
    presc = prescription_service.sign_prescription(
        db, presc, current_user.id, payload.signature_method
    )
    audit_service.log_action(
        db, current_user.id, "sign", "prescription", presc.id, current_user.tenant_id
    )
    return presc


@router.get("/{presc_id}", response_model=PrescriptionResponse)
def get_prescription(
    presc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    presc = db.query(Prescription).filter(Prescription.id == presc_id).first()
    if not presc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return presc


@router.get("/visit/{visit_id}", response_model=list[PrescriptionResponse])
def list_by_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Prescription).filter(Prescription.visit_id == visit_id).all()


@router.post("/voice-parse")
def parse_voice(
    payload: VoicePrescriptionRequest,
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, [Role.doctor, Role.super_admin])
    items = parse_voice_prescription(payload.text)
    return {"items": items, "language": payload.language}
