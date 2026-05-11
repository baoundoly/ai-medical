from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    appointment_type: str = "regular"
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    tenant_id: int


class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    appointment_type: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: int
    tenant_id: int
    status: str
    token_number: Optional[int] = None
    queue_position: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    total: int
    items: list[AppointmentResponse]


class QueueResponse(BaseModel):
    id: int
    tenant_id: int
    date: datetime
    doctor_id: int
    current_token: int
    total_tokens: int

    class Config:
        from_attributes = True
