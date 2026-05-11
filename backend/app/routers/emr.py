"""
EMR (Electronic Medical Record) router — full patient timeline view.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.appointment import Appointment
from app.models.lab_report import LabReport
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.user import Role, User
from app.models.visit import Visit
from app.models.vitals import VitalSigns

router = APIRouter(prefix="/emr", tags=["EMR"])


@router.get("/patient/{patient_id}")
def patient_emr(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the full EMR for a patient: visits, prescriptions, labs, vitals."""
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.tenant_id == current_user.tenant_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    visits = db.query(Visit).filter(Visit.patient_id == patient_id).order_by(Visit.visit_date.desc()).all()
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient_id).all()
    lab_reports = db.query(LabReport).filter(LabReport.patient_id == patient_id).all()
    vitals = db.query(VitalSigns).filter(VitalSigns.patient_id == patient_id).all()
    appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).all()

    return {
        "patient_id": patient_id,
        "patient_uid": patient.patient_uid,
        "name": patient.name,
        "total_visits": len(visits),
        "visits": [{"id": v.id, "date": str(v.visit_date), "status": v.status} for v in visits],
        "prescriptions": [{"id": p.id, "status": p.status} for p in prescriptions],
        "lab_reports": [{"id": r.id, "type": r.report_type, "critical": r.is_critical} for r in lab_reports],
        "vitals": [{"id": v.id, "recorded_at": str(v.recorded_at)} for v in vitals],
        "appointments": [{"id": a.id, "scheduled_at": str(a.scheduled_at)} for a in appointments],
    }
