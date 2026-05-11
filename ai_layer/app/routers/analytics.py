from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.appointment import Appointment
from app.models.billing import Invoice
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.user import Role, User
from app.models.visit import Visit

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin])
    tenant_id = current_user.tenant_id

    total_patients = db.query(func.count(Patient.id)).filter(
        Patient.tenant_id == tenant_id, Patient.is_active == True
    ).scalar()

    total_visits = db.query(func.count(Visit.id)).filter(
        Visit.tenant_id == tenant_id
    ).scalar()

    total_prescriptions = db.query(func.count(Prescription.id)).filter(
        Prescription.doctor_id.in_(
            db.query(User.id).filter(User.tenant_id == tenant_id)
        )
    ).scalar()

    total_revenue = db.query(func.sum(Invoice.net_amount)).filter(
        Invoice.tenant_id == tenant_id, Invoice.status == "paid"
    ).scalar() or 0.0

    return {
        "tenant_id": tenant_id,
        "total_patients": total_patients,
        "total_visits": total_visits,
        "total_prescriptions": total_prescriptions,
        "total_revenue": float(total_revenue),
    }


@router.get("/appointments/by-day")
def appointments_by_day(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin])
    rows = (
        db.query(
            func.date(Appointment.scheduled_at).label("day"),
            func.count(Appointment.id).label("count"),
        )
        .filter(Appointment.tenant_id == current_user.tenant_id)
        .group_by(func.date(Appointment.scheduled_at))
        .order_by(func.date(Appointment.scheduled_at).desc())
        .limit(30)
        .all()
    )
    return [{"day": str(r.day), "count": r.count} for r in rows]
