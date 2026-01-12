from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserResponse


class FriendRequestCreate(BaseModel):
    email: EmailStr


class FriendshipResponse(BaseModel):
    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: str
    friend_group_id: Optional[UUID] = None
    created_at: datetime
    accepted_at: Optional[datetime] = None
    friend: UserResponse  # The other user (not current user)

    class Config:
        from_attributes = True


class FriendResponse(BaseModel):
    id: UUID
    email: str
    name: str
    profile_picture: Optional[str] = None
    friendship_id: UUID
    friend_group_id: Optional[UUID] = None
    balance: float = 0  # Net balance with this friend

    class Config:
        from_attributes = True


class FriendListResponse(BaseModel):
    friends: List[FriendResponse]
    pending_sent: List[FriendshipResponse]
    pending_received: List[FriendshipResponse]
