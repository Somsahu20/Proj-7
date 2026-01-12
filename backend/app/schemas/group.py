from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserResponse


class GroupCategory(str):
    TRIP = "trip"
    APARTMENT = "apartment"
    COUPLE = "couple"
    FRIENDS = "friends"
    FAMILY = "family"
    PROJECT = "project"
    OTHER = "other"


# ==================== GROUP SCHEMAS ====================
class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., max_length=50)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = None
    settings: Optional[dict] = None


class GroupResponse(GroupBase):
    id: UUID
    image_url: Optional[str] = None
    created_by_id: UUID
    is_archived: bool
    settings: dict = {}
    created_at: datetime
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    creator: UserResponse
    members: List["MemberResponse"] = []
    total_expenses: float = 0
    your_balance: float = 0

    class Config:
        from_attributes = True


# ==================== MEMBERSHIP SCHEMAS ====================
class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    group_id: UUID
    role: str
    joined_at: datetime
    is_active: bool
    user: UserResponse

    class Config:
        from_attributes = True


class MemberAdd(BaseModel):
    email: EmailStr


class MemberRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|member)$")


# ==================== INVITATION SCHEMAS ====================
class InvitationCreate(BaseModel):
    email: EmailStr


class InvitationResponse(BaseModel):
    id: UUID
    group_id: UUID
    email: str
    status: str
    expires_at: datetime
    created_at: datetime
    group_name: Optional[str] = None
    invited_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class InvitationAccept(BaseModel):
    token: str


GroupDetailResponse.model_rebuild()
