from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import Role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Role = Role.patient
    tenant_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    mfa_enabled: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]
