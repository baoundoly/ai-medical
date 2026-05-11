from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role, check_tenant_access
from app.database import get_db
from app.models.patient import MergeRequest, Patient, PatientAllergy
from app.models.user import Role, User
from app.schemas.patient import (
    AllergyCreate,
    AllergyResponse,
    DuplicateCheckRequest,
    MergeRequestCreate,
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.services import audit_service, patient_service

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.receptionist, Role.assistant, Role.doctor])
    check_tenant_access(current_user, payload.tenant_id)

    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    uid = patient_service.generate_patient_uid(db, tenant.code, "DHK")
    patient = Patient(
        **payload.model_dump(),
        patient_uid=uid,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    audit_service.log_action(
        db, current_user.id, "create", "patient", patient.id, payload.tenant_id
    )
    return patient


@router.get("/", response_model=PatientListResponse)
def list_patients(
    skip: int = 0,
    limit: int = 20,
    search: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.assistant,
                               Role.receptionist, Role.nurse, Role.pharmacist])
    query = db.query(Patient).filter(
        Patient.tenant_id == current_user.tenant_id,
        Patient.is_active == True,
    )
    if search:
        query = query.filter(
            Patient.name.ilike(f"%{search}%") | Patient.patient_uid.ilike(f"%{search}%")
        )
    total = query.count()
    items = query.order_by(Patient.id.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.tenant_id == current_user.tenant_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.assistant, Role.receptionist])
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.tenant_id == current_user.tenant_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    old = {c.name: getattr(patient, c.name) for c in patient.__table__.columns}
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    audit_service.log_action(
        db, current_user.id, "update", "patient", patient.id, current_user.tenant_id,
        old_values=old, new_values=payload.model_dump(exclude_none=True),
    )
    return patient


@router.post("/check-duplicates")
def check_duplicates(
    payload: DuplicateCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    duplicates = patient_service.check_duplicate_patients(
        db, current_user.tenant_id, payload.name, payload.mobile, payload.dob
    )
    return {"count": len(duplicates), "patients": [p.id for p in duplicates]}


@router.post("/{patient_id}/allergies", response_model=AllergyResponse, status_code=201)
def add_allergy(
    patient_id: int,
    payload: AllergyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.nurse, Role.assistant])
    patient = db.query(Patient).filter(
        Patient.id == patient_id, Patient.tenant_id == current_user.tenant_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    allergy = PatientAllergy(
        patient_id=patient_id,
        noted_by_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(allergy)
    db.commit()
    db.refresh(allergy)
    return allergy


@router.get("/{patient_id}/allergies", response_model=list[AllergyResponse])
def list_allergies(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(PatientAllergy).filter(PatientAllergy.patient_id == patient_id).all()


@router.post("/merge", status_code=202)
def request_merge(
    payload: MergeRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin])
    merge = MergeRequest(
        tenant_id=current_user.tenant_id,
        source_patient_id=payload.source_patient_id,
        target_patient_id=payload.target_patient_id,
        requested_by_id=current_user.id,
        reason=payload.reason,
    )
    db.add(merge)
    db.commit()
    return {"message": "Merge request submitted for review", "merge_id": merge.id}
