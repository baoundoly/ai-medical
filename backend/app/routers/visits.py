from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.user import Role, User
from app.models.visit import Symptom, Visit
from app.schemas.visit import (
    SymptomCreate,
    SymptomResponse,
    VisitApprove,
    VisitCreate,
    VisitListResponse,
    VisitResponse,
    VisitUpdate,
)
from app.services import audit_service

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.post("/", response_model=VisitResponse, status_code=201)
def create_visit(
    payload: VisitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.assistant])
    visit = Visit(
        **payload.model_dump(),
        assistant_id=current_user.id if current_user.role == Role.assistant else None,
        visit_date=datetime.now(timezone.utc),
        status="open",
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    audit_service.log_action(db, current_user.id, "create", "visit", visit.id, payload.tenant_id)
    return visit


@router.get("/", response_model=VisitListResponse)
def list_visits(
    patient_id: int = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Visit).filter(Visit.tenant_id == current_user.tenant_id)
    if patient_id:
        query = query.filter(Visit.patient_id == patient_id)
    total = query.count()
    items = query.order_by(Visit.visit_date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{visit_id}", response_model=VisitResponse)
def get_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    visit = db.query(Visit).filter(
        Visit.id == visit_id, Visit.tenant_id == current_user.tenant_id
    ).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@router.patch("/{visit_id}", response_model=VisitResponse)
def update_visit(
    visit_id: int,
    payload: VisitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.assistant])
    visit = db.query(Visit).filter(
        Visit.id == visit_id, Visit.tenant_id == current_user.tenant_id
    ).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    if visit.doctor_approved_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Visit is finalized and cannot be modified",
        )
    # Assistants may not set diagnosis
    if current_user.role == Role.assistant and payload.status == "approved":
        raise HTTPException(status_code=403, detail="Assistants cannot approve visits")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(visit, field, value)
    db.commit()
    db.refresh(visit)
    audit_service.log_action(db, current_user.id, "update", "visit", visit.id, current_user.tenant_id)
    return visit


@router.post("/{visit_id}/approve", response_model=VisitResponse)
def approve_visit(
    visit_id: int,
    payload: VisitApprove,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.doctor, Role.super_admin])
    visit = db.query(Visit).filter(
        Visit.id == visit_id, Visit.tenant_id == current_user.tenant_id
    ).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    if visit.doctor_approved_at:
        raise HTTPException(status_code=400, detail="Visit already approved")
    visit.doctor_approved_at = datetime.now(timezone.utc)
    visit.doctor_approved_by = current_user.id
    visit.status = "approved"
    db.commit()
    db.refresh(visit)
    audit_service.log_action(db, current_user.id, "approve", "visit", visit.id, current_user.tenant_id)
    return visit


@router.post("/{visit_id}/symptoms", response_model=SymptomResponse, status_code=201)
def add_symptom(
    visit_id: int,
    payload: SymptomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.assistant])
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    if visit.doctor_approved_at:
        raise HTTPException(status_code=403, detail="Visit is finalized")
    symptom = Symptom(visit_id=visit_id, **payload.model_dump(exclude={"visit_id"}))
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    return symptom


@router.get("/{visit_id}/symptoms", response_model=list[SymptomResponse])
def list_symptoms(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Symptom).filter(Symptom.visit_id == visit_id).all()
