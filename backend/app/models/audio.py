from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AudioRecord(Base):
    __tablename__ = "audio_records"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    duration_seconds = Column(Float, nullable=True)
    file_url = Column(String(512), nullable=True)
    language = Column(String(10), default="bn")  # bn=Bangla, en=English
    status = Column(String(20), default="pending")  # pending/processing/completed/failed
    consent_given = Column(Boolean, default=False)
    consent_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    visit = relationship("Visit", back_populates="audio_records")
    transcription = relationship("Transcription", back_populates="audio_record", uselist=False)
    ai_summaries = relationship("AISummary", back_populates="audio_record")


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_records.id"), nullable=False, unique=True)
    raw_text = Column(Text, nullable=True)
    processed_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    language = Column(String(10), default="bn")
    created_at = Column(DateTime, default=datetime.utcnow)

    audio_record = relationship("AudioRecord", back_populates="transcription")
    segments = relationship("TranscriptionSegment", back_populates="transcription", cascade="all, delete-orphan")


class TranscriptionSegment(Base):
    __tablename__ = "transcription_segments"

    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=False, index=True)
    speaker = Column(String(20), nullable=False)  # PATIENT/ASSISTANT/DOCTOR
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)

    transcription = relationship("Transcription", back_populates="segments")


class AISummary(Base):
    __tablename__ = "ai_summaries"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    audio_id = Column(Integer, ForeignKey("audio_records.id"), nullable=True)
    chief_complaint = Column(Text, nullable=True)
    symptoms_json = Column(Text, nullable=True)           # JSON list of symptoms
    diagnoses_json = Column(Text, nullable=True)          # JSON list of diagnosis suggestions
    prescription_suggestions_json = Column(Text, nullable=True)  # JSON list of medicine suggestions
    confidence_score = Column(Float, nullable=True)
    doctor_reviewed = Column(Boolean, default=False)
    doctor_corrections_json = Column(Text, nullable=True)  # Doctor's corrections for retraining
    created_at = Column(DateTime, default=datetime.utcnow)

    visit = relationship("Visit", back_populates="ai_summaries")
    audio_record = relationship("AudioRecord", back_populates="ai_summaries")
