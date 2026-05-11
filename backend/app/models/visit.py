from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assistant_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    visit_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), default="pending")  # pending/in_progress/completed
    chief_complaint = Column(Text, nullable=True)
    hpi = Column(Text, nullable=True)            # History of Present Illness
    ros = Column(Text, nullable=True)            # Review of Systems
    past_history = Column(Text, nullable=True)
    family_history = Column(Text, nullable=True)
    social_history = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    doctor_approved_at = Column(DateTime, nullable=True)
    doctor_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    patient = relationship("Patient", back_populates="visits")
    doctor = relationship("User", foreign_keys=[doctor_id])
    assistant = relationship("User", foreign_keys=[assistant_id])
    approving_doctor = relationship("User", foreign_keys=[doctor_approved_by])
    symptoms = relationship("Symptom", back_populates="visit", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="visit")
    lab_reports = relationship("LabReport", back_populates="visit")
    vitals = relationship("VitalSigns", back_populates="visit")
    audio_records = relationship("AudioRecord", back_populates="visit")
    ai_summaries = relationship("AISummary", back_populates="visit")
    invoices = relationship("Invoice", back_populates="visit")


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    duration = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    frequency = Column(String(100), nullable=True)
    associated_symptoms = Column(Text, nullable=True)
    source = Column(String(20), default="manual")  # voice/manual
    confidence_score = Column(Float, nullable=True)

    visit = relationship("Visit", back_populates="symptoms")
