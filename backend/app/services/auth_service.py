from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_backup_codes,
    generate_mfa_secret,
    get_password_hash,
    get_totp_uri,
    verify_password,
    verify_totp,
)
from app.models.user import User, UserDevice


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Return user if credentials are valid, else None."""
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_tokens(user: User) -> dict:
    """Generate access and refresh tokens for the given user."""
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "tenant_id": user.tenant_id,
    }
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 60 * 30,  # 30 minutes in seconds
    }


def refresh_access_token(db: Session, refresh_token: str) -> Optional[dict]:
    """Validate a refresh token and issue new access + refresh tokens."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if not user:
        return None
    return create_tokens(user)


def setup_mfa(db: Session, user: User) -> dict:
    """Enable MFA for user — generate secret, QR URI and backup codes."""
    secret = generate_mfa_secret()
    backup_codes = generate_backup_codes()
    user.mfa_secret = secret
    user.mfa_enabled = True
    db.commit()
    return {
        "secret": secret,
        "qr_uri": get_totp_uri(secret, user.email),
        "backup_codes": backup_codes,
    }


def disable_mfa(db: Session, user: User):
    """Disable MFA for user."""
    user.mfa_secret = None
    user.mfa_enabled = False
    db.commit()


def verify_mfa_code(user: User, code: str) -> bool:
    """Return True if the TOTP code is valid for the user's MFA secret."""
    if not user.mfa_secret:
        return False
    return verify_totp(user.mfa_secret, code)


def register_device(
    db: Session,
    user: User,
    fingerprint: str,
    ip_address: str = None,
) -> UserDevice:
    """Register or update a device for a user."""
    device = (
        db.query(UserDevice)
        .filter(UserDevice.user_id == user.id, UserDevice.device_fingerprint == fingerprint)
        .first()
    )
    if not device:
        device = UserDevice(
            user_id=user.id,
            device_fingerprint=fingerprint,
            ip_address=ip_address,
            last_seen=datetime.utcnow(),
        )
        db.add(device)
    else:
        device.last_seen = datetime.utcnow()
        if ip_address:
            device.ip_address = ip_address
    db.commit()
    db.refresh(device)
    return device


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    role: str,
    tenant_id: Optional[int] = None,
) -> User:
    """Create a new user with hashed password."""
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role,
        tenant_id=tenant_id,
        is_active=True,
        mfa_enabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
