from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.pharmacy import Dispensing, Medicine
from app.models.user import Role, User
from app.schemas.pharmacy import (
    DispensingCreate,
    DispensingResponse,
    MedicineCreate,
    MedicineListResponse,
    MedicineResponse,
    MedicineUpdate,
    StockUpdateRequest,
)
from app.services import audit_service

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])


@router.post("/medicines", response_model=MedicineResponse, status_code=201)
def create_medicine(
    payload: MedicineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.pharmacist])
    med = Medicine(**payload.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    audit_service.log_action(
        db, current_user.id, "create", "medicine", med.id, current_user.tenant_id
    )
    return med


@router.get("/medicines", response_model=MedicineListResponse)
def list_medicines(
    search: str = None,
    low_stock: bool = False,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Medicine).filter(Medicine.tenant_id == current_user.tenant_id)
    if search:
        safe = search.replace("%", r"\%").replace("_", r"\_")
        query = query.filter(
            Medicine.name.ilike(f"%{safe}%") | Medicine.generic_name.ilike(f"%{safe}%")
        )
    if low_stock:
        query = query.filter(Medicine.stock_quantity <= Medicine.reorder_level)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/medicines/{med_id}", response_model=MedicineResponse)
def get_medicine(
    med_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    med = db.query(Medicine).filter(
        Medicine.id == med_id, Medicine.tenant_id == current_user.tenant_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return med


@router.patch("/medicines/{med_id}", response_model=MedicineResponse)
def update_medicine(
    med_id: int,
    payload: MedicineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.pharmacist])
    med = db.query(Medicine).filter(
        Medicine.id == med_id, Medicine.tenant_id == current_user.tenant_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(med, field, value)
    db.commit()
    db.refresh(med)
    return med


@router.post("/medicines/{med_id}/stock", response_model=MedicineResponse)
def update_stock(
    med_id: int,
    payload: StockUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin, Role.pharmacist])
    med = db.query(Medicine).filter(
        Medicine.id == med_id, Medicine.tenant_id == current_user.tenant_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    med.stock_quantity += payload.quantity_change
    if med.stock_quantity < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    db.commit()
    db.refresh(med)
    audit_service.log_action(
        db, current_user.id, "stock_update", "medicine", med.id, current_user.tenant_id,
        details=f"change={payload.quantity_change}",
    )
    return med


@router.post("/dispense", response_model=DispensingResponse, status_code=201)
def dispense(
    payload: DispensingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.pharmacist, Role.super_admin])
    dispensing = Dispensing(
        prescription_id=payload.prescription_id,
        dispensed_by_id=current_user.id,
        items_json=payload.items_json,
        notes=payload.notes,
    )
    db.add(dispensing)
    db.commit()
    db.refresh(dispensing)
    return dispensing
