from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.billing import Invoice, Payment
from app.models.user import Role, User
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    RefundRequest,
)
from app.services import audit_service

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/invoices", response_model=InvoiceResponse, status_code=201)
def create_invoice(
    payload: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.receptionist])
    net = payload.total_amount - payload.discount + payload.tax_amount
    invoice = Invoice(**payload.model_dump(), net_amount=net, status="pending")
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    audit_service.log_action(
        db, current_user.id, "create", "invoice", invoice.id, payload.tenant_id
    )
    return invoice


@router.get("/invoices", response_model=InvoiceListResponse)
def list_invoices(
    patient_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Invoice).filter(Invoice.tenant_id == current_user.tenant_id)
    if patient_id:
        query = query.filter(Invoice.patient_id == patient_id)
    if status:
        query = query.filter(Invoice.status == status)
    total = query.count()
    items = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/payments", response_model=PaymentResponse, status_code=201)
def process_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.receptionist])
    invoice = db.query(Invoice).filter(Invoice.id == payload.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    payment = Payment(**payload.model_dump(), status="completed")
    db.add(payment)
    invoice.status = "paid"
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/refund")
def process_refund(
    payload: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin])
    invoice = db.query(Invoice).filter(Invoice.id == payload.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = "refunded"
    payment = Payment(
        invoice_id=payload.invoice_id,
        amount=-abs(payload.amount),
        payment_method="refund",
        transaction_id=f"REFUND-{invoice.id}",
        status="refunded",
    )
    db.add(payment)
    db.commit()
    audit_service.log_action(
        db, current_user.id, "refund", "invoice", invoice.id, current_user.tenant_id,
        details=payload.reason,
    )
    return {"message": "Refund processed", "invoice_id": invoice.id}
