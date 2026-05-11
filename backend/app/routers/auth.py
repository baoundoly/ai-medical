from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import check_role
from app.database import get_db
from app.models.user import Role, User
from app.schemas.auth import (
    LoginRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    RefreshTokenRequest,
    SessionResponse,
    TokenResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="MFA verification required",
            headers={"X-MFA-Required": "true"},
        )
    if payload.device_fingerprint:
        ip = request.client.host if request.client else None
        auth_service.register_device(db, user, payload.device_fingerprint, ip)
    tokens = auth_service.create_tokens(user)
    return tokens


@router.post("/login/mfa", response_model=TokenResponse)
def login_mfa(
    payload: LoginRequest,
    mfa: MFAVerifyRequest,
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not auth_service.verify_mfa_code(user, mfa.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    tokens = auth_service.refresh_access_token(db, payload.refresh_token)
    if not tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return tokens


@router.post("/mfa/setup", response_model=MFASetupResponse)
def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = auth_service.setup_mfa(db, current_user)
    return result


@router.post("/mfa/disable")
def disable_mfa(
    mfa: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not auth_service.verify_mfa_code(current_user, mfa.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code")
    auth_service.disable_mfa(db, current_user)
    return {"message": "MFA disabled"}


@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.user import UserDevice
    devices = (
        db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    )
    return devices
