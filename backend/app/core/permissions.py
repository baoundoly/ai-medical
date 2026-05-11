from functools import wraps
from typing import Callable

from fastapi import HTTPException, status

from app.models.user import Role

# Define what each role can access
ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.super_admin: {
        "all",  # Super admin can do everything
    },
    Role.hospital_admin: {
        "user:read", "user:create", "user:update",
        "patient:read", "patient:create", "patient:update",
        "visit:read", "visit:create", "visit:update",
        "prescription:read",
        "lab_report:read",
        "vitals:read",
        "appointment:read", "appointment:create", "appointment:update",
        "analytics:read",
        "pharmacy:read", "pharmacy:create", "pharmacy:update",
        "billing:read", "billing:create", "billing:update",
        "audit:read",
        "merge_patient:approve",
    },
    Role.doctor: {
        "patient:read", "patient:update",
        "visit:read", "visit:create", "visit:update", "visit:approve",
        "prescription:read", "prescription:create", "prescription:sign",
        "lab_report:read",
        "vitals:read",
        "appointment:read",
        "audio:read",
        "emr:read",
        "diagnosis:create",
    },
    Role.assistant: {
        "patient:read", "patient:create",
        "visit:read", "visit:create",
        "vitals:read", "vitals:create",
        "audio:create", "audio:read",
        "appointment:read", "appointment:create",
        "lab_report:upload",
    },
    Role.receptionist: {
        "patient:read", "patient:create", "patient:update",
        "appointment:read", "appointment:create", "appointment:update",
        "billing:read", "billing:create",
    },
    Role.nurse: {
        "patient:read",
        "vitals:read", "vitals:create",
        "visit:read",
    },
    Role.lab_technician: {
        "lab_report:read", "lab_report:create", "lab_report:upload",
        "patient:read",
        "visit:read",
    },
    Role.pharmacist: {
        "prescription:read",
        "pharmacy:read", "pharmacy:update",
        "pharmacy:dispense",
        "patient:read",
    },
    Role.patient: {
        "own_data:read",
    },
}

# Fields that assistants are blocked from setting
ASSISTANT_BLOCKED_FIELDS = {"diagnosis", "prescription", "doctor_approved_at"}

# Fields that are immutable after visit finalization
IMMUTABLE_AFTER_FINALIZATION = {
    "chief_complaint", "hpi", "ros", "past_history",
    "family_history", "social_history",
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    perms = ROLE_PERMISSIONS.get(role, set())
    return "all" in perms or permission in perms


def require_permission(permission: str):
    """Dependency factory that enforces a specific permission."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # The current_user is injected as a kwarg via FastAPI dependency
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission} required",
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_role(current_user, allowed_roles: list[str]):
    """Raise 403 if user's role is not in allowed_roles."""
    if current_user.role not in allowed_roles and current_user.role != Role.super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Allowed roles: {allowed_roles}",
        )


def check_tenant_access(current_user, tenant_id: int):
    """Raise 403 if user does not belong to the given tenant."""
    if current_user.role == Role.super_admin:
        return
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cross-tenant access not allowed",
        )
