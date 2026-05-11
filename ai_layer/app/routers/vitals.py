from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.user import Role, User
from app.models.vitals import NewsScore, VitalSigns
from app.schemas.vitals import VitalSignsCreate, VitalSignsResponse

router = APIRouter(prefix="/vitals", tags=["Vitals"])


def _calculate_news2(vitals: VitalSigns) -> int:
    """
    Calculate NEWS2 score (0-20) from vital sign values.
    Returns integer score.
    """
    score = 0

    # Respiratory rate
    rr = vitals.respiratory_rate
    if rr is not None:
        if rr <= 8 or rr >= 25:
            score += 3
        elif rr >= 21:
            score += 2
        elif rr <= 11:
            score += 1

    # SpO2 (scale 1)
    spo2 = vitals.spo2
    if spo2 is not None:
        if spo2 <= 91:
            score += 3
        elif spo2 <= 93:
            score += 2
        elif spo2 <= 95:
            score += 1

    # Systolic BP
    sbp = vitals.bp_systolic
    if sbp is not None:
        if sbp <= 90 or sbp >= 220:
            score += 3
        elif sbp <= 100:
            score += 2
        elif sbp <= 110:
            score += 1

    # Pulse
    pulse = vitals.pulse
    if pulse is not None:
        if pulse <= 40 or pulse >= 131:
            score += 3
        elif pulse >= 111:
            score += 2
        elif pulse <= 50 or pulse >= 91:
            score += 1

    # Consciousness (AVPU)
    consciousness = vitals.consciousness
    if consciousness and consciousness.upper() != "A":
        score += 3

    # Temperature
    temp = vitals.temperature
    if temp is not None:
        if temp <= 35.0:
            score += 3
        elif temp >= 39.1:
            score += 2
        elif temp <= 36.0 or temp >= 38.1:
            score += 1

    return score


def _news_risk(score: int) -> str:
    if score >= 7:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


@router.post("/", response_model=VitalSignsResponse, status_code=201)
def record_vitals(
    payload: VitalSignsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.nurse, Role.assistant])
    # Compute BMI
    bmi = None
    if payload.weight and payload.height and payload.height > 0:
        height_m = payload.height / 100
        bmi = round(payload.weight / (height_m ** 2), 1)

    vitals = VitalSigns(
        **payload.model_dump(),
        recorded_by_id=current_user.id,
        bmi=bmi,
    )
    db.add(vitals)
    db.flush()

    news_score_val = _calculate_news2(vitals)
    risk = _news_risk(news_score_val)
    news = NewsScore(
        vital_id=vitals.id,
        score=news_score_val,
        risk_level=risk,
    )
    db.add(news)
    db.commit()
    db.refresh(vitals)
    return vitals


@router.get("/visit/{visit_id}", response_model=list[VitalSignsResponse])
def get_vitals_by_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(VitalSigns)
        .filter(VitalSigns.visit_id == visit_id)
        .order_by(VitalSigns.recorded_at.desc())
        .all()
    )


@router.get("/{vital_id}", response_model=VitalSignsResponse)
def get_vitals(
    vital_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vitals = db.query(VitalSigns).filter(VitalSigns.id == vital_id).first()
    if not vitals:
        raise HTTPException(status_code=404, detail="Vitals record not found")
    return vitals
