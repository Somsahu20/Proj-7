# Notification Models

## NotificationType Enum

```python
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
```

## NotificationResponse

```python
class NotificationResponse(BaseModel):
    id: UUID
    type: NotificationType
    title: str
    body: str
    data: dict = {}
    action_url: Optional[str]
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
```

## NotificationList

```python
class NotificationList(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int
    pagination: dict
```

## UnreadCount

```python
class UnreadCount(BaseModel):
    unread_count: int
    by_type: dict[str, int]
```

## NotificationCreate (Internal)

```python
class NotificationCreate(BaseModel):
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    data: dict = {}
    action_url: Optional[str] = None
    send_email: bool = True
```

## SSE Event Models

```python
class SSEEvent(BaseModel):
    event: str
    data: dict
    id: Optional[str] = None

class BalanceUpdateEvent(BaseModel):
    group_id: UUID
    user_id: UUID
    old_balance: Decimal
    new_balance: Decimal
    change: Decimal
    reason: str

class ExpenseEvent(BaseModel):
    group_id: UUID
    expense: dict  # ExpenseResponse as dict

class PaymentEvent(BaseModel):
    group_id: UUID
    payment: dict  # PaymentResponse as dict
```
