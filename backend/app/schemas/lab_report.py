from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LabResultBase(BaseModel):
    test_name: str
    value: str
    unit: Optional[str] = None
    normal_range: Optional[str] = None
    is_abnormal: bool = False


class LabResultCreate(LabResultBase):
    pass


class LabResultResponse(LabResultBase):
    id: int
    report_id: int

    class Config:
        from_attributes = True


class LabReportBase(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    report_type: str


class LabReportCreate(LabReportBase):
    pass


class LabReportResponse(LabReportBase):
    id: int
    uploaded_by_id: int
    file_url: Optional[str] = None
    ocr_text: Optional[str] = None
    ai_analysis: Optional[str] = None
    is_critical: bool
    critical_alert_sent: bool
    uploaded_at: datetime
    results: list[LabResultResponse] = []

    class Config:
        from_attributes = True


class LabReportListResponse(BaseModel):
    total: int
    items: list[LabReportResponse]
