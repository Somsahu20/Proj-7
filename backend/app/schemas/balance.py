from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID
from decimal import Decimal


# ==================== BALANCE SCHEMAS ====================
class UserBalance(BaseModel):
    user_id: UUID
    user_name: str
    user_email: str
    balance: Decimal  # Positive = owed to you, Negative = you owe
    profile_picture: Optional[str] = None


class GroupBalanceSummary(BaseModel):
    group_id: UUID
    group_name: str
    your_total_balance: Decimal
    balances: List[UserBalance]


class DetailedBalance(BaseModel):
    user_id: UUID
    user_name: str
    owes_you: Decimal
    you_owe: Decimal
    net_balance: Decimal


class BalanceResponse(BaseModel):
    total_balance: Decimal  # Overall: positive = you're owed, negative = you owe
    you_are_owed: Decimal
    you_owe: Decimal
    group_balances: List[GroupBalanceSummary]


# ==================== SETTLEMENT SCHEMAS ====================
class SettlementSuggestion(BaseModel):
    from_user_id: UUID
    from_user_name: str
    to_user_id: UUID
    to_user_name: str
    amount: Decimal


class GroupSettlementResponse(BaseModel):
    group_id: UUID
    group_name: str
    suggestions: List[SettlementSuggestion]
    total_transactions: int
    original_transactions: int  # Before optimization


class DebtSimplificationResult(BaseModel):
    original_debts: List[Dict]
    simplified_debts: List[SettlementSuggestion]
    transactions_saved: int


# ==================== BALANCE DETAIL ====================
class BalanceWithUser(BaseModel):
    user: "UserResponse"
    balance: Decimal
    transactions: List[Dict]  # Recent transactions between users

    class Config:
        from_attributes = True


from app.schemas.user import UserResponse
BalanceWithUser.model_rebuild()
