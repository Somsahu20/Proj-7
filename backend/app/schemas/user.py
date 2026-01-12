from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# ==================== AUTH SCHEMAS ====================
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class GoogleAuthRequest(BaseModel):
    code: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# ==================== USER SCHEMAS ====================
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: bool
    is_verified: bool
    reliability_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    notification_preferences: dict = {}
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferencesUpdate(BaseModel):
    expense_added: bool = True
    expense_edited: bool = True
    expense_deleted: bool = True
    payment_received: bool = True
    payment_confirmed: bool = True
    added_to_group: bool = True
    balance_reminder: bool = True
    weekly_digest: bool = True
    digest_day: str = "monday"


# Forward reference update
TokenResponse.model_rebuild()
