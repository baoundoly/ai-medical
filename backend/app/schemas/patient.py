from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class PatientBase(BaseModel):
    name: str
    mobile: Optional[str] = None
    nid: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class PatientCreate(PatientBase):
    tenant_id: int


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    nid: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class PatientResponse(PatientBase):
    id: int
    tenant_id: int
    patient_uid: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    total: int
    items: list[PatientResponse]


class AllergyBase(BaseModel):
    allergen: str
    severity: Optional[str] = None
    reaction: Optional[str] = None


class AllergyCreate(AllergyBase):
    pass


class AllergyResponse(AllergyBase):
    id: int
    patient_id: int
    noted_by_id: Optional[int] = None
    noted_at: datetime

    class Config:
        from_attributes = True


class DuplicateCheckRequest(BaseModel):
    mobile: Optional[str] = None
    name: str
    dob: Optional[date] = None


class MergeRequestCreate(BaseModel):
    source_patient_id: int
    target_patient_id: int
    reason: Optional[str] = None
