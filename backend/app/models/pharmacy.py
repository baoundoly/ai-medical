from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    generic_name = Column(String(255), nullable=True)
    strength = Column(String(100), nullable=True)
    form = Column(String(50), nullable=True)  # tablet/capsule/syrup/injection
    stock_quantity = Column(Integer, default=0)
    unit_price = Column(Float, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    barcode = Column(String(100), nullable=True, unique=True)
    reorder_level = Column(Integer, default=10)

    dispensings = relationship("Dispensing", back_populates="medicine_ref", foreign_keys="Dispensing.medicine_id")


class Dispensing(Base):
    __tablename__ = "dispensings"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=True)
    dispensed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dispensed_at = Column(DateTime, default=datetime.utcnow)
    items_json = Column(Text, nullable=True)  # JSON of dispensed items with quantities
    notes = Column(Text, nullable=True)

    prescription = relationship("Prescription", back_populates="dispensings")
    medicine_ref = relationship("Medicine", back_populates="dispensings", foreign_keys=[medicine_id])
    dispensed_by = relationship("User", foreign_keys=[dispensed_by_id])
