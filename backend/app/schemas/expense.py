from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from app.schemas.user import UserResponse


class ExpenseCategory(str):
    FOOD = "food"
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    UTILITIES = "utilities"
    GROCERIES = "groceries"
    HEALTHCARE = "healthcare"
    OTHER = "other"


# ==================== SPLIT SCHEMAS ====================
class SplitCreate(BaseModel):
    user_id: UUID
    amount: Optional[Decimal] = None
    shares: Optional[int] = None
    percentage: Optional[Decimal] = None


class SplitResponse(BaseModel):
    id: UUID
    expense_id: UUID
    user_id: UUID
    amount: Decimal
    shares: Optional[int] = None
    percentage: Optional[Decimal] = None
    is_settled: bool
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# ==================== EXPENSE SCHEMAS ====================
class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0)
    date: date
    category: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class ExpenseCreate(ExpenseBase):
    group_id: UUID
    payer_id: UUID
    split_type: str = Field(..., pattern="^(equal|unequal|shares|percentage)$")
    splits: List[SplitCreate] = []
    participant_ids: Optional[List[UUID]] = None  # For equal splits

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class ExpenseUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[date] = None
    category: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    payer_id: Optional[UUID] = None
    split_type: Optional[str] = Field(None, pattern="^(equal|unequal|shares|percentage)$")
    splits: Optional[List[SplitCreate]] = None
    participant_ids: Optional[List[UUID]] = None


class ExpenseResponse(ExpenseBase):
    id: UUID
    group_id: UUID
    payer_id: UUID
    split_type: str
    receipt_url: Optional[str] = None
    created_by_id: UUID
    is_deleted: bool
    approval_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    payer: Optional[UserResponse] = None
    splits: List[SplitResponse] = []
    comment_count: int = 0
    reaction_count: int = 0

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    expenses: List[ExpenseResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ExpenseFilter(BaseModel):
    category: Optional[str] = None
    payer_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = None


# ==================== EXPENSE TEMPLATE SCHEMAS ====================
class ExpenseTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    group_id: Optional[UUID] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    split_type: Optional[str] = None
    split_data: dict = {}


class ExpenseTemplateResponse(BaseModel):
    id: UUID
    name: str
    group_id: Optional[UUID] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    split_type: Optional[str] = None
    split_data: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True
