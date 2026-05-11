from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AudioRecordBase(BaseModel):
    visit_id: int
    language: str = "bn"


class AudioRecordCreate(AudioRecordBase):
    pass


class ConsentRequest(BaseModel):
    consent_given: bool


class TranscriptionSegmentResponse(BaseModel):
    id: int
    transcription_id: int
    speaker: str
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class TranscriptionResponse(BaseModel):
    id: int
    audio_id: int
    raw_text: Optional[str] = None
    processed_text: Optional[str] = None
    confidence_score: Optional[float] = None
    language: str
    created_at: datetime
    segments: list[TranscriptionSegmentResponse] = []

    class Config:
        from_attributes = True


class AISummaryResponse(BaseModel):
    id: int
    visit_id: int
    audio_id: Optional[int] = None
    chief_complaint: Optional[str] = None
    symptoms_json: Optional[str] = None
    diagnoses_json: Optional[str] = None
    prescription_suggestions_json: Optional[str] = None
    confidence_score: Optional[float] = None
    doctor_reviewed: bool
    doctor_corrections_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AudioRecordResponse(AudioRecordBase):
    id: int
    duration_seconds: Optional[float] = None
    file_url: Optional[str] = None
    status: str
    consent_given: bool
    consent_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TranscriptionCorrectionRequest(BaseModel):
    corrections: str
    corrected_text: Optional[str] = None
