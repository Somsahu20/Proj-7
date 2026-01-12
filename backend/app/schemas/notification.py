from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    # Transaction
    EXPENSE_ADDED = 'expense_added'
    EXPENSE_EDITED = 'expense_edited'
    EXPENSE_DELETED = 'expense_deleted'
    PAYMENT_RECEIVED = 'payment_received'
    PAYMENT_CONFIRMED = 'payment_confirmed'
    PAYMENT_REJECTED = 'payment_rejected'

    # Group
    ADDED_TO_GROUP = 'added_to_group'
    REMOVED_FROM_GROUP = 'removed_from_group'
    GROUP_INVITATION = 'group_invitation'
    MEMBER_JOINED = 'member_joined'
    MEMBER_LEFT = 'member_left'

    # Balance
    BALANCE_REMINDER = 'balance_reminder'
    SETTLEMENT_SUGGESTION = 'settlement_suggestion'
    DEBT_CLEARED = 'debt_cleared'

    # Social
    EXPENSE_COMMENT = 'expense_comment'
    EXPENSE_REACTION = 'expense_reaction'
    MENTIONED = 'mentioned'


# ==================== NOTIFICATION SCHEMAS ====================
class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    body: str
    data: dict = {}
    action_url: Optional[str] = None
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int
    total: int
    page: int
    per_page: int


class UnreadCountResponse(BaseModel):
    unread_count: int
    by_type: Dict[str, int] = {}


class MarkReadRequest(BaseModel):
    notification_ids: List[UUID]


# ==================== SSE EVENTS ====================
class SSEEvent(BaseModel):
    event: str
    data: dict
    id: Optional[str] = None


class BalanceUpdateEvent(BaseModel):
    group_id: UUID
    user_id: UUID
    old_balance: float
    new_balance: float
    change: float
    reason: str


class ExpenseEvent(BaseModel):
    group_id: UUID
    expense: dict


class PaymentEvent(BaseModel):
    group_id: UUID
    payment: dict
