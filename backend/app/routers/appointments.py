from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.appointment import Appointment, Queue
from app.models.user import Role, User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentUpdate,
    QueueResponse,
)
from app.services import audit_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _assign_token(db: Session, appointment: Appointment) -> int:
    """Assign a queue token. Emergency appointments get token 0."""
    if appointment.appointment_type == "emergency":
        return 0
    existing = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.tenant_id == appointment.tenant_id,
            Appointment.status != "cancelled",
        )
        .count()
    )
    return existing + 1


@router.post("/", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    payload: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.receptionist, Role.assistant])
    appt = Appointment(**payload.model_dump(), status="scheduled")
    db.add(appt)
    db.flush()
    appt.token_number = _assign_token(db, appt)
    db.commit()
    db.refresh(appt)
    audit_service.log_action(
        db, current_user.id, "create", "appointment", appt.id, payload.tenant_id
    )
    return appt


@router.get("/", response_model=AppointmentListResponse)
def list_appointments(
    doctor_id: int = None,
    patient_id: int = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Appointment).filter(Appointment.tenant_id == current_user.tenant_id)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    total = query.count()
    items = query.order_by(Appointment.scheduled_at.asc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{appt_id}", response_model=AppointmentResponse)
def get_appointment(
    appt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = db.query(Appointment).filter(
        Appointment.id == appt_id, Appointment.tenant_id == current_user.tenant_id
    ).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.patch("/{appt_id}", response_model=AppointmentResponse)
def update_appointment(
    appt_id: int,
    payload: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.receptionist, Role.assistant])
    appt = db.query(Appointment).filter(
        Appointment.id == appt_id, Appointment.tenant_id == current_user.tenant_id
    ).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(appt, field, value)
    db.commit()
    db.refresh(appt)
    return appt


@router.get("/queue/today", response_model=list[AppointmentResponse])
def today_queue(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = datetime.utcnow().date()
    appts = (
        db.query(Appointment)
        .filter(
            Appointment.tenant_id == current_user.tenant_id,
            Appointment.doctor_id == doctor_id,
            Appointment.status != "cancelled",
        )
        .order_by(Appointment.token_number.asc())
        .all()
    )
    return appts
