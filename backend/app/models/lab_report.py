from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(100), nullable=False)  # CBC, LFT, RFT, ECG, etc.
    file_url = Column(String(512), nullable=True)
    ocr_text = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    is_critical = Column(Boolean, default=False)
    critical_alert_sent = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    visit = relationship("Visit", back_populates="lab_reports")
    patient = relationship("Patient", back_populates="lab_reports")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    results = relationship("LabResult", back_populates="report", cascade="all, delete-orphan")


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("lab_reports.id"), nullable=False, index=True)
    test_name = Column(String(255), nullable=False)
    value = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    normal_range = Column(String(100), nullable=True)
    is_abnormal = Column(Boolean, default=False)

    report = relationship("LabReport", back_populates="results")
