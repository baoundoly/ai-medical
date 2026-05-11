from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VitalSignsBase(BaseModel):
    visit_id: int
    patient_id: int
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    pulse: Optional[int] = None
    temperature: Optional[float] = None
    spo2: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    respiratory_rate: Optional[int] = None
    consciousness: Optional[str] = None


class VitalSignsCreate(VitalSignsBase):
    pass


class NewsScoreResponse(BaseModel):
    id: int
    vital_id: int
    score: int
    risk_level: str
    calculated_at: datetime

    class Config:
        from_attributes = True


class VitalSignsResponse(VitalSignsBase):
    id: int
    recorded_by_id: int
    bmi: Optional[float] = None
    recorded_at: datetime
    news_score: Optional[NewsScoreResponse] = None

    class Config:
        from_attributes = True
