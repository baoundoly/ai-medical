from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)  # CREATE/UPDATE/DELETE/LOGIN/LOGOUT
    resource_type = Column(String(100), nullable=True)  # Patient/Visit/Prescription etc.
    resource_id = Column(Integer, nullable=True)
    old_value_json = Column(Text, nullable=True)
    new_value_json = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
