"""
Audio intake router: upload consent, trigger transcription + AI summarisation.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.audio import AISummary, AudioRecord, Transcription, TranscriptionSegment
from app.models.user import Role, User
from app.schemas.audio import (
    AISummaryResponse,
    AudioRecordResponse,
    ConsentRequest,
    TranscriptionCorrectionRequest,
    TranscriptionResponse,
)
from app.services.ai_service import (
    calculate_confidence,
    extract_clinical_history,
    suggest_diagnosis,
    transcribe_audio,
)

router = APIRouter(prefix="/audio", tags=["Audio Intake"])


@router.post("/", response_model=AudioRecordResponse, status_code=201)
def create_audio_record(
    visit_id: int,
    language: str = "bn",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.assistant])
    record = AudioRecord(
        visit_id=visit_id,
        language=language,
        status="pending",
        consent_given=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/{audio_id}/consent", response_model=AudioRecordResponse)
def set_consent(
    audio_id: int,
    payload: ConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(AudioRecord).filter(AudioRecord.id == audio_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Audio record not found")
    record.consent_given = payload.consent_given
    record.consent_time = datetime.utcnow() if payload.consent_given else None
    db.commit()
    db.refresh(record)
    return record


@router.post("/{audio_id}/transcribe", response_model=TranscriptionResponse)
def transcribe(
    audio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger transcription for an audio record (stub — uses file_url if set)."""
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.doctor, Role.assistant])
    record = db.query(AudioRecord).filter(AudioRecord.id == audio_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Audio record not found")
    if not record.consent_given:
        raise HTTPException(status_code=403, detail="Patient consent not obtained")

    result = transcribe_audio(record.file_url or "", record.language)
    transcription = Transcription(
        audio_id=audio_id,
        raw_text=result["text"],
        processed_text=result["text"],
        confidence_score=result["confidence"],
        language=result["language"],
    )
    db.add(transcription)
    record.status = "transcribed"
    db.commit()
    db.refresh(transcription)
    return transcription


@router.post("/{audio_id}/summarise", response_model=AISummaryResponse)
def summarise(
    audio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate AI clinical summary from the latest transcription."""
    check_role(current_user, [Role.super_admin, Role.doctor, Role.assistant])
    record = db.query(AudioRecord).filter(AudioRecord.id == audio_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Audio record not found")
    transcription = (
        db.query(Transcription)
        .filter(Transcription.audio_id == audio_id)
        .order_by(Transcription.id.desc())
        .first()
    )
    if not transcription:
        raise HTTPException(status_code=400, detail="No transcription available")

    clinical = extract_clinical_history(transcription.processed_text or "")
    diagnoses = suggest_diagnosis(clinical["symptoms"])
    confidence = calculate_confidence(
        clinical["symptoms"], diagnoses, transcription.confidence_score
    )

    import json
    summary = AISummary(
        visit_id=record.visit_id,
        audio_id=audio_id,
        chief_complaint=clinical["chief_complaint"],
        symptoms_json=json.dumps(clinical["symptoms"]),
        diagnoses_json=json.dumps(diagnoses),
        prescription_suggestions_json=json.dumps([]),
        confidence_score=confidence,
        doctor_reviewed=False,
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


@router.post("/{audio_id}/corrections", response_model=AISummaryResponse)
def submit_corrections(
    audio_id: int,
    payload: TranscriptionCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Doctor submits corrections on the AI summary (stored for retraining)."""
    check_role(current_user, [Role.doctor, Role.super_admin])
    summary = (
        db.query(AISummary)
        .filter(AISummary.audio_id == audio_id)
        .order_by(AISummary.id.desc())
        .first()
    )
    if not summary:
        raise HTTPException(status_code=404, detail="No AI summary found")
    summary.doctor_corrections_json = payload.corrections
    summary.doctor_reviewed = True
    db.commit()
    db.refresh(summary)
    return summary
