from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from app.schemas.user import UserResponse


# ==================== PAYMENT SCHEMAS ====================
class PaymentCreate(BaseModel):
    group_id: UUID
    receiver_id: UUID
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=200)
    payment_method: Optional[str] = Field(None, max_length=50)
    date: date


class PaymentUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    payment_method: Optional[str] = Field(None, max_length=50)


class PaymentResponse(BaseModel):
    id: UUID
    group_id: UUID
    payer_id: UUID
    receiver_id: UUID
    amount: Decimal
    description: Optional[str] = None
    payment_method: Optional[str] = None
    date: date
    status: str
    confirmed_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    created_at: datetime
    payer: Optional[UserResponse] = None
    receiver: Optional[UserResponse] = None
    proofs: List["PaymentProofResponse"] = []

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    payments: List[PaymentResponse]
    total: int
    page: int
    per_page: int


# ==================== PAYMENT PROOF SCHEMAS ====================
class PaymentProofResponse(BaseModel):
    id: UUID
    payment_id: UUID
    file_url: str
    file_type: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ==================== PAYMENT ACTIONS ====================
class PaymentConfirm(BaseModel):
    pass  # Just needs to be called


class PaymentReject(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class PaymentCancel(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)


PaymentResponse.model_rebuild()
