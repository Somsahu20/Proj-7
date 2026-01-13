from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import date


# ==================== CATEGORY ANALYTICS ====================
class CategorySpending(BaseModel):
    category: str
    amount: Decimal
    percentage: Decimal
    expense_count: int


# ==================== TIME SERIES ANALYTICS ====================
class SpendingDataPoint(BaseModel):
    date: date
    amount: Decimal
    expense_count: int


# ==================== MEMBER ANALYTICS ====================
class MemberContribution(BaseModel):
    user_id: UUID
    user_name: str
    profile_picture: Optional[str] = None
    total_paid: Decimal       # Total amount they paid for group
    total_share: Decimal      # Their share of expenses
    net_contribution: Decimal # paid - share (positive = overpaid)


# ==================== FRIEND ANALYTICS ====================
class FriendSpending(BaseModel):
    friend_id: UUID
    friend_name: str
    profile_picture: Optional[str] = None
    total_spent: Decimal
    expense_count: int


# ==================== GROUP ANALYTICS RESPONSE ====================
class GroupAnalyticsResponse(BaseModel):
    group_id: UUID
    group_name: str
    period: str
    start_date: date
    end_date: date
    total_spending: Decimal
    expense_count: int
    category_breakdown: List[CategorySpending]
    spending_over_time: List[SpendingDataPoint]
    member_contributions: List[MemberContribution]
    average_expense: Decimal
    top_category: Optional[str] = None


# ==================== FRIENDS ANALYTICS RESPONSE ====================
class FriendsAnalyticsResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_spending: Decimal
    expense_count: int
    category_breakdown: List[CategorySpending]
    spending_over_time: List[SpendingDataPoint]
    friend_breakdown: List[FriendSpending]
    average_expense: Decimal
    top_category: Optional[str] = None
