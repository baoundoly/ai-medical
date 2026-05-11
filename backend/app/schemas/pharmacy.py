from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MedicineBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    form: Optional[str] = None
    unit_price: Optional[float] = None
    reorder_level: int = 10


class MedicineCreate(MedicineBase):
    tenant_id: int
    stock_quantity: int = 0
    barcode: Optional[str] = None


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    form: Optional[str] = None
    unit_price: Optional[float] = None
    reorder_level: Optional[int] = None


class StockUpdateRequest(BaseModel):
    quantity_change: int  # Positive to add, negative to reduce
    reason: Optional[str] = None


class MedicineResponse(MedicineBase):
    id: int
    tenant_id: int
    stock_quantity: int
    expiry_date: Optional[datetime] = None
    barcode: Optional[str] = None

    class Config:
        from_attributes = True


class MedicineListResponse(BaseModel):
    total: int
    items: list[MedicineResponse]


class DispensingCreate(BaseModel):
    prescription_id: int
    items_json: str  # JSON string of dispensed items
    notes: Optional[str] = None


class DispensingResponse(BaseModel):
    id: int
    prescription_id: int
    dispensed_by_id: int
    dispensed_at: datetime
    items_json: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
