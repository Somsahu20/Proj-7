# Notification Types

## Overview

The app sends notifications for various events. Users can control which notifications they receive through preferences.

---

## Notification Categories

### Transaction Notifications

| Event | In-App | Email Default | Description |
|-------|--------|---------------|-------------|
| `expense_added` | ✅ | ON | New expense added to group |
| `expense_edited` | ✅ | ON | Expense you're part of was modified |
| `expense_deleted` | ✅ | ON | Expense you're part of was deleted |
| `payment_received` | ✅ | ON | Someone recorded a payment to you |
| `payment_confirmed` | ✅ | ON | Your payment was confirmed |
| `payment_rejected` | ✅ | OFF | Your payment was rejected |

### Group Notifications

| Event | In-App | Email Default | Description |
|-------|--------|---------------|-------------|
| `added_to_group` | ✅ | ON | You were added to a new group |
| `removed_from_group` | ✅ | ON | You were removed from a group |
| `group_invitation` | ✅ | ON | You're invited to join a group |
| `member_joined` | ✅ | OFF | New member joined group |
| `member_left` | ✅ | OFF | Member left the group |
| `group_settings_changed` | ✅ | OFF | Group settings were modified |

### Balance Notifications

| Event | In-App | Email Default | Description |
|-------|--------|---------------|-------------|
| `balance_reminder` | ✅ | ON | Periodic reminder about debts |
| `settlement_suggestion` | ✅ | ON | Optimized settlement available |
| `debt_cleared` | ✅ | ON | All debts in group settled |
| `group_settled` | ✅ | ON | Entire group is settled |

### Social Notifications

| Event | In-App | Email Default | Description |
|-------|--------|---------------|-------------|
| `expense_comment` | ✅ | ON | Someone commented on expense |
| `expense_reaction` | ✅ | OFF | Someone reacted to expense |
| `mentioned` | ✅ | ON | You were @mentioned |
| `reply_to_comment` | ✅ | ON | Reply to your comment |

---

## Notification Data Structure

### In-App Notification

```json
{
  "id": "notification-uuid",
  "type": "expense_added",
  "title": "New expense in Trip to Paris",
  "body": "John added 'Dinner at restaurant' ($120.00)",
  "data": {
    "group_id": "group-uuid",
    "group_name": "Trip to Paris",
    "expense_id": "expense-uuid",
    "expense_description": "Dinner at restaurant",
    "expense_amount": 120.00,
    "actor_id": "user-uuid",
    "actor_name": "John Doe"
  },
  "action_url": "/groups/uuid/expenses/uuid",
  "is_read": false,
  "created_at": "2026-01-11T20:00:00Z"
}
```

---

## View Notifications

### Technical Requirements

**Request**
```
GET /api/v1/notifications
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20)
  - is_read: boolean (optional filter)
  - type: string (optional filter)
```

**Response**
```json
HTTP 200 OK
{
  "notifications": [
    {
      "id": "uuid-1",
      "type": "expense_added",
      "title": "New expense in Trip to Paris",
      "body": "John added 'Dinner at restaurant' ($120.00)",
      "action_url": "/groups/uuid/expenses/uuid",
      "is_read": false,
      "created_at": "2026-01-11T20:00:00Z"
    },
    {
      "id": "uuid-2",
      "type": "payment_received",
      "title": "Payment received",
      "body": "Bob recorded a $50.00 payment to you",
      "action_url": "/groups/uuid/payments/uuid",
      "is_read": true,
      "created_at": "2026-01-11T15:00:00Z"
    }
  ],
  "unread_count": 5,
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

## Mark as Read

### Single Notification

**Request**
```
POST /api/v1/notifications/{notification_id}/read
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "id": "uuid",
  "is_read": true
}
```

### Mark All as Read

**Request**
```
POST /api/v1/notifications/read-all
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "marked_read": 15,
  "message": "All notifications marked as read"
}
```

---

## Unread Count

### Technical Requirements

**Request**
```
GET /api/v1/notifications/unread-count
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "unread_count": 5,
  "by_type": {
    "expense_added": 2,
    "payment_received": 1,
    "expense_comment": 2
  }
}
```

---

## Real-time Notifications (SSE)

### SSE Event Format

```json
{
  "event": "notification:new",
  "data": {
    "id": "notification-uuid",
    "type": "expense_added",
    "title": "New expense in Trip to Paris",
    "body": "John added 'Dinner at restaurant' ($120.00)",
    "action_url": "/groups/uuid/expenses/uuid",
    "created_at": "2026-01-11T20:00:00Z"
  }
}
```

### Connection

```javascript
const eventSource = new EventSource('/api/v1/notifications/stream', {
  headers: { 'Authorization': `Bearer ${token}` }
});

eventSource.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  showNotificationToast(notification);
  incrementBadge();
};
```

---

## Notification Triggers

### Expense Added

**Trigger**: New expense created
**Recipients**: All participants except the creator
**Content**:
```
Title: New expense in {group_name}
Body: {actor_name} added '{expense_description}' (${amount})
       Your share: ${my_share}
```

### Payment Received

**Trigger**: Payment recorded with you as receiver
**Recipients**: Receiver only
**Content**:
```
Title: Payment from {payer_name}
Body: {payer_name} recorded a ${amount} payment to you in {group_name}.
       Please confirm if you received this payment.
```

### Payment Confirmed

**Trigger**: Payment confirmed by receiver
**Recipients**: Payer only
**Content**:
```
Title: Payment confirmed
Body: {receiver_name} confirmed your ${amount} payment.
       Your balance in {group_name} has been updated.
```

### Added to Group

**Trigger**: User added to a group
**Recipients**: The added user
**Content**:
```
Title: You've been added to {group_name}
Body: {inviter_name} added you to {group_name}.
       Current balance: ${balance}
```

---

## Delete Notifications

### Single Notification

**Request**
```
DELETE /api/v1/notifications/{notification_id}
Authorization: Bearer <access_token>
```

### Delete All Read

**Request**
```
DELETE /api/v1/notifications?read=true
Authorization: Bearer <access_token>
```

---

## Acceptance Criteria

### View Notifications
- [ ] All notification types displayed
- [ ] Unread count accurate
- [ ] Pagination works
- [ ] Filters work correctly

### Mark as Read
- [ ] Single notification can be marked
- [ ] All notifications can be marked
- [ ] Unread count updates

### Real-time
- [ ] SSE connection established
- [ ] New notifications received
- [ ] UI updates without refresh

### Triggers
- [ ] All events trigger notifications
- [ ] Correct recipients receive them
- [ ] Content is accurate
