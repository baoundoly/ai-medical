from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VisitBase(BaseModel):
    patient_id: int
    doctor_id: Optional[int] = None
    chief_complaint: Optional[str] = None
    hpi: Optional[str] = None
    ros: Optional[str] = None
    past_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None


class VisitCreate(VisitBase):
    tenant_id: int


class VisitUpdate(BaseModel):
    chief_complaint: Optional[str] = None
    hpi: Optional[str] = None
    ros: Optional[str] = None
    past_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    status: Optional[str] = None


class VisitApprove(BaseModel):
    corrections: Optional[str] = None


class VisitResponse(VisitBase):
    id: int
    tenant_id: int
    assistant_id: Optional[int] = None
    visit_date: datetime
    status: str
    ai_summary: Optional[str] = None
    doctor_approved_at: Optional[datetime] = None
    doctor_approved_by: Optional[int] = None

    class Config:
        from_attributes = True


class VisitListResponse(BaseModel):
    total: int
    items: list[VisitResponse]


class SymptomBase(BaseModel):
    name: str
    duration: Optional[str] = None
    severity: Optional[str] = None
    frequency: Optional[str] = None
    associated_symptoms: Optional[str] = None
    source: str = "manual"


class SymptomCreate(SymptomBase):
    visit_id: int


class SymptomResponse(SymptomBase):
    id: int
    visit_id: int
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True
