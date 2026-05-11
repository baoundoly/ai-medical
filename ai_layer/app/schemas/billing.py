from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InvoiceBase(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    total_amount: float
    discount: float = 0.0
    tax_amount: float = 0.0
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    tenant_id: int


class InvoiceResponse(InvoiceBase):
    id: int
    tenant_id: int
    net_amount: float
    status: str
    payment_method: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    total: int
    items: list[InvoiceResponse]


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    processed_at: datetime

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    invoice_id: int
    amount: float
    reason: str
