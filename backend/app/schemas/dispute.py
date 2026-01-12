from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ==================== DISPUTE SCHEMAS ====================
class DisputeCreate(BaseModel):
    expense_id: Optional[UUID] = None
    payment_id: Optional[UUID] = None
    reason: str = Field(..., max_length=50)
    description: str = Field(..., min_length=10, max_length=2000)
    evidence_urls: List[str] = []


class DisputeResponse(BaseModel):
    id: UUID
    expense_id: Optional[UUID] = None
    payment_id: Optional[UUID] = None
    opened_by_id: UUID
    reason: str
    description: str
    evidence_urls: List[str] = []
    status: str
    resolution: Optional[str] = None
    resolved_by_id: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    voting_ends_at: Optional[datetime] = None
    created_at: datetime
    votes: List["DisputeVoteResponse"] = []
    vote_summary: Optional[dict] = None

    class Config:
        from_attributes = True


class DisputeVoteCreate(BaseModel):
    vote: str = Field(..., pattern="^(approve|reject|abstain)$")
    comment: Optional[str] = Field(None, max_length=500)


class DisputeVoteResponse(BaseModel):
    id: UUID
    dispute_id: UUID
    user_id: UUID
    vote: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DisputeResolve(BaseModel):
    resolution: str = Field(..., pattern="^(upheld|dismissed|modified)$")
    resolution_notes: Optional[str] = Field(None, max_length=2000)


DisputeResponse.model_rebuild()
