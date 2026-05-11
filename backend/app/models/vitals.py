from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class VitalSigns(Base):
    __tablename__ = "vital_signs"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bp_systolic = Column(Integer, nullable=True)
    bp_diastolic = Column(Integer, nullable=True)
    pulse = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)   # Celsius
    spo2 = Column(Integer, nullable=True)         # Oxygen saturation %
    weight = Column(Float, nullable=True)          # kg
    height = Column(Float, nullable=True)          # cm
    bmi = Column(Float, nullable=True)
    respiratory_rate = Column(Integer, nullable=True)  # breaths/min
    consciousness = Column(String(20), nullable=True)  # Alert/Voice/Pain/Unresponsive
    recorded_at = Column(DateTime, default=datetime.utcnow)

    visit = relationship("Visit", back_populates="vitals")
    patient = relationship("Patient", back_populates="vitals")
    recorded_by = relationship("User", foreign_keys=[recorded_by_id])
    news_score = relationship("NewsScore", back_populates="vital", uselist=False)


class NewsScore(Base):
    __tablename__ = "news_scores"

    id = Column(Integer, primary_key=True, index=True)
    vital_id = Column(Integer, ForeignKey("vital_signs.id"), nullable=False, unique=True)
    score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)  # Low/Medium/High
    calculated_at = Column(DateTime, default=datetime.utcnow)

    vital = relationship("VitalSigns", back_populates="news_score")
