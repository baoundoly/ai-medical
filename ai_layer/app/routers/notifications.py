from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.audit import AuditLog
from app.models.user import Role, User
from app.services.audit_service import get_audit_logs

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def list_notifications(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    In-app notifications: return recent audit log entries for the current user's tenant
    that affect them (stub implementation using audit log as notification source).
    """
    total, logs = get_audit_logs(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    items = [
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "created_at": str(log.timestamp),
        }
        for log in logs
    ]
    return {"total": total, "items": items}


@router.get("/audit-log")
def audit_log(
    resource_type: str = None,
    resource_id: int = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_role(current_user, [Role.super_admin, Role.hospital_admin])
    total, logs = get_audit_logs(
        db,
        tenant_id=current_user.tenant_id,
        resource_type=resource_type,
        resource_id=resource_id,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "items": [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "created_at": str(log.timestamp),
        }
        for log in logs
    ]}
