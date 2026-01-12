from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserResponse


# ==================== COMMENT SCHEMAS ====================
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[UUID] = None
    mentions: List[UUID] = []


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: UUID
    expense_id: UUID
    user_id: UUID
    parent_id: Optional[UUID] = None
    content: str
    mentions: List[UUID] = []
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


# ==================== REACTION SCHEMAS ====================
class ReactionCreate(BaseModel):
    emoji: str = Field(..., min_length=1, max_length=10)


class ReactionResponse(BaseModel):
    id: UUID
    expense_id: UUID
    user_id: UUID
    emoji: str
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class ReactionSummary(BaseModel):
    emoji: str
    count: int
    users: List[UserResponse] = []


# ==================== ACTIVITY SCHEMAS ====================
class ActivityResponse(BaseModel):
    id: UUID
    group_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    data: dict = {}
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    activities: List[ActivityResponse]
    total: int
    page: int
    per_page: int


CommentResponse.model_rebuild()
