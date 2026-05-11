from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="draft")  # draft/approved/dispensed
    signed_at = Column(DateTime, nullable=True)
    signature_method = Column(String(20), nullable=True)  # password/biometric/otp
    digital_signature_hash = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    visit = relationship("Visit", back_populates="prescriptions")
    patient = relationship("Patient")
    doctor = relationship("User", foreign_keys=[doctor_id])
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")
    drug_interactions = relationship("DrugInteractionAlert", back_populates="prescription", cascade="all, delete-orphan")
    dispensings = relationship("Dispensing", back_populates="prescription")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    medicine_name = Column(String(255), nullable=False)
    generic_name = Column(String(255), nullable=True)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)  # OD, BD, TDS, QDS
    duration = Column(String(100), nullable=True)
    meal_instruction = Column(String(100), nullable=True)  # before/after meals
    route = Column(String(50), nullable=True)  # oral/IV/IM/topical

    prescription = relationship("Prescription", back_populates="items")


class DrugInteractionAlert(Base):
    __tablename__ = "drug_interaction_alerts"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    drug1 = Column(String(255), nullable=False)
    drug2 = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)  # LOW/MODERATE/HIGH/CRITICAL
    message = Column(Text, nullable=False)

    prescription = relationship("Prescription", back_populates="drug_interactions")
