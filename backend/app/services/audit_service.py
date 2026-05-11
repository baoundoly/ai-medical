from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: int,
    tenant_id: int,
    ip_address: str = None,
    old_values: dict = None,
    new_values: dict = None,
    details: str = None,
) -> AuditLog:
    """Create an audit log entry for any state-changing action."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        tenant_id=tenant_id,
        ip_address=ip_address,
        old_value_json=str(old_values) if old_values else None,
        new_value_json=str(new_values) if new_values else details,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_audit_logs(
    db: Session,
    tenant_id: int,
    resource_type: str = None,
    resource_id: int = None,
    user_id: int = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[int, list[AuditLog]]:
    """Query audit logs with optional filters."""
    query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if resource_id is not None:
        query = query.filter(AuditLog.resource_id == resource_id)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    total = query.count()
    items = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return total, items
