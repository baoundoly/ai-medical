from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PrescriptionItemBase(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    meal_instruction: Optional[str] = None
    route: Optional[str] = "oral"


class PrescriptionItemCreate(PrescriptionItemBase):
    pass


class PrescriptionItemResponse(PrescriptionItemBase):
    id: int
    prescription_id: int

    class Config:
        from_attributes = True


class PrescriptionBase(BaseModel):
    visit_id: int
    patient_id: int
    doctor_id: int


class PrescriptionCreate(PrescriptionBase):
    items: list[PrescriptionItemCreate] = []


class PrescriptionSignRequest(BaseModel):
    signature_method: str  # password/biometric/otp
    credential: str        # password, OTP code, or biometric token


class DrugInteractionResponse(BaseModel):
    id: int
    prescription_id: int
    drug1: str
    drug2: str
    severity: str
    message: str

    class Config:
        from_attributes = True


class PrescriptionResponse(PrescriptionBase):
    id: int
    status: str
    signed_at: Optional[datetime] = None
    signature_method: Optional[str] = None
    created_at: datetime
    items: list[PrescriptionItemResponse] = []
    drug_interactions: list[DrugInteractionResponse] = []

    class Config:
        from_attributes = True


class VoicePrescriptionRequest(BaseModel):
    text: str
    language: str = "bn"
