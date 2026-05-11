from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    patient_uid = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    mobile = Column(String(20), nullable=True, index=True)
    nid = Column(String(30), nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    blood_group = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="patients")
    allergies = relationship("PatientAllergy", back_populates="patient", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    lab_reports = relationship("LabReport", back_populates="patient")
    vitals = relationship("VitalSigns", back_populates="patient")
    invoices = relationship("Invoice", back_populates="patient")


class PatientAllergy(Base):
    __tablename__ = "patient_allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    allergen = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    reaction = Column(Text, nullable=True)
    noted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    noted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="allergies")
    noted_by = relationship("User", foreign_keys=[noted_by_id])


class MergeRequest(Base):
    __tablename__ = "merge_requests"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    source_patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    target_patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    source_patient = relationship("Patient", foreign_keys=[source_patient_id])
    target_patient = relationship("Patient", foreign_keys=[target_patient_id])
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
