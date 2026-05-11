from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=False)
    appointment_type = Column(String(30), default="regular")  # regular/emergency/follow_up/online
    status = Column(String(20), default="scheduled")  # scheduled/in_progress/completed/cancelled/no_show
    token_number = Column(Integer, nullable=True)
    queue_position = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id])


class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    current_token = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    doctor = relationship("User", foreign_keys=[doctor_id])
