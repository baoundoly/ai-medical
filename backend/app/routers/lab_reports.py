from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.lab_report import LabReport, LabResult
from app.models.user import Role, User
from app.schemas.lab_report import (
    LabReportCreate,
    LabReportListResponse,
    LabReportResponse,
    LabResultCreate,
)
from app.services import audit_service
from app.services.notification_service import send_critical_lab_alert

# Critical lab thresholds used for auto-flagging
CRITICAL_THRESHOLDS = {
    "platelet": lambda v: float(v) < 20000,
    "troponin": lambda v: float(v) > 0.4,
    "glucose": lambda v: float(v) < 40 or float(v) > 500,
}

router = APIRouter(prefix="/lab-reports", tags=["Lab Reports"])


def _check_critical(results: list[LabResult]) -> bool:
    """Return True if any result value exceeds a critical threshold."""
    for result in results:
        for keyword, check_fn in CRITICAL_THRESHOLDS.items():
            if keyword in result.test_name.lower():
                try:
                    if check_fn(result.value):
                        return True
                except (ValueError, TypeError):
                    pass
    return False


@router.post("/", response_model=LabReportResponse, status_code=201)
def create_lab_report(
    payload: LabReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.lab_technician, Role.doctor])
    report = LabReport(
        **payload.model_dump(),
        uploaded_by_id=current_user.id,
        is_critical=False,
        critical_alert_sent=False,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    audit_service.log_action(
        db, current_user.id, "create", "lab_report", report.id, current_user.tenant_id
    )
    return report


@router.post("/{report_id}/results", response_model=LabReportResponse)
def add_results(
    report_id: int,
    results: list[LabResultCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.lab_technician, Role.doctor])
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    result_objs = []
    for r in results:
        obj = LabResult(report_id=report_id, **r.model_dump())
        db.add(obj)
        result_objs.append(obj)
    db.flush()
    report.is_critical = _check_critical(result_objs)
    if report.is_critical and not report.critical_alert_sent:
        # Send critical alert to ordering doctor (visit doctor or uploader)
        send_critical_lab_alert(
            current_user.id, f"Patient#{report.patient_id}",
            result_objs[0].test_name if result_objs else "Unknown", "Critical"
        )
        report.critical_alert_sent = True
    db.commit()
    db.refresh(report)
    return report


@router.get("/", response_model=LabReportListResponse)
def list_reports(
    patient_id: int = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(LabReport)
    if patient_id:
        query = query.filter(LabReport.patient_id == patient_id)
    total = query.count()
    items = query.order_by(LabReport.uploaded_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{report_id}", response_model=LabReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    return report
