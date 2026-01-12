# Notification Preferences

## Overview

Users can configure which email notifications they receive and how often they receive digest emails. The app sends email notifications only (no push or SMS).

---

## Notification Categories

### Transaction Notifications

| Notification | Default | Description |
|--------------|---------|-------------|
| `expense_added` | ON | When a new expense is added to a group you're in |
| `expense_edited` | ON | When an expense you're part of is modified |
| `expense_deleted` | ON | When an expense you're part of is deleted |
| `payment_received` | ON | When someone records a payment to you |
| `payment_confirmed` | ON | When your payment is confirmed by receiver |
| `payment_rejected` | OFF | When your payment is rejected by receiver |

### Group Notifications

| Notification | Default | Description |
|--------------|---------|-------------|
| `added_to_group` | ON | When you're added to a new group |
| `removed_from_group` | ON | When you're removed from a group |
| `member_joined` | OFF | When a new member joins your group |
| `member_left` | OFF | When a member leaves your group |
| `group_settings_changed` | OFF | When group settings are modified |

### Balance Notifications

| Notification | Default | Description |
|--------------|---------|-------------|
| `balance_reminder` | ON | Periodic reminder about outstanding debts |
| `settlement_suggestion` | ON | When optimal settlement is calculated |
| `debt_cleared` | ON | When all debts in a group are settled |

### Social Notifications

| Notification | Default | Description |
|--------------|---------|-------------|
| `expense_comment` | ON | When someone comments on your expense |
| `expense_reaction` | OFF | When someone reacts to your expense |
| `mentioned` | ON | When you're mentioned in a comment |

---

## Email Digest Settings

### Digest Frequency Options

| Option | Description |
|--------|-------------|
| `off` | No digest, only instant notifications |
| `daily` | Daily summary at configured time |
| `weekly` | Weekly summary on configured day |

### Digest Content
When digest is enabled, certain notifications are batched:
- New expenses in groups
- Member changes
- Non-urgent balance updates

Urgent notifications are always sent immediately:
- Payment received (requires approval)
- Added to group
- Mentioned in comment

---

## View Preferences

### User Story
> As a user, I want to see my current notification settings so that I know what emails I'll receive.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/notification-preferences
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "email_enabled": true,
  "digest": {
    "frequency": "daily",
    "time": "09:00",
    "timezone": "America/New_York"
  },
  "notifications": {
    "expense_added": true,
    "expense_edited": true,
    "expense_deleted": true,
    "payment_received": true,
    "payment_confirmed": true,
    "payment_rejected": false,
    "added_to_group": true,
    "removed_from_group": true,
    "member_joined": false,
    "member_left": false,
    "group_settings_changed": false,
    "balance_reminder": true,
    "settlement_suggestion": true,
    "debt_cleared": true,
    "expense_comment": true,
    "expense_reaction": false,
    "mentioned": true
  },
  "reminder_settings": {
    "enabled": true,
    "frequency_days": 7,
    "min_amount": 10.00
  }
}
```

---

## Update Preferences

### User Story
> As a user, I want to customize my notification settings so that I only receive emails I care about.

### Technical Requirements

**Request**
```json
PATCH /api/v1/users/me/notification-preferences
Authorization: Bearer <access_token>
{
  "email_enabled": true,
  "digest": {
    "frequency": "weekly",
    "day": "monday",
    "time": "08:00",
    "timezone": "Europe/London"
  },
  "notifications": {
    "expense_added": true,
    "member_joined": true,
    "expense_reaction": true
  }
}
```

Note: Only include fields you want to update.

**Response**
```json
HTTP 200 OK
{
  "message": "Preferences updated",
  "email_enabled": true,
  "digest": {
    "frequency": "weekly",
    "day": "monday",
    "time": "08:00",
    "timezone": "Europe/London"
  },
  "notifications": {
    "expense_added": true,
    "expense_edited": true,
    "expense_deleted": true,
    "payment_received": true,
    "payment_confirmed": true,
    "payment_rejected": false,
    "added_to_group": true,
    "removed_from_group": true,
    "member_joined": true,
    "member_left": false,
    "group_settings_changed": false,
    "balance_reminder": true,
    "settlement_suggestion": true,
    "debt_cleared": true,
    "expense_comment": true,
    "expense_reaction": true,
    "mentioned": true
  }
}
```

---

## Disable All Emails

### User Story
> As a user, I want to turn off all email notifications if I don't want to receive any.

### Technical Requirements

**Request**
```json
PATCH /api/v1/users/me/notification-preferences
Authorization: Bearer <access_token>
{
  "email_enabled": false
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "All email notifications disabled",
  "email_enabled": false
}
```

Note: When `email_enabled` is false, no emails are sent regardless of individual settings.

---

## Reminder Configuration

### User Story
> As a user, I want to configure payment reminders so that I'm reminded about outstanding debts.

### Settings

| Setting | Type | Description |
|---------|------|-------------|
| `enabled` | boolean | Whether to receive reminders |
| `frequency_days` | int | Days between reminders (3, 7, 14, 30) |
| `min_amount` | decimal | Only remind if debt exceeds this amount |

### Technical Requirements

**Request**
```json
PATCH /api/v1/users/me/notification-preferences
Authorization: Bearer <access_token>
{
  "reminder_settings": {
    "enabled": true,
    "frequency_days": 14,
    "min_amount": 25.00
  }
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "Reminder settings updated",
  "reminder_settings": {
    "enabled": true,
    "frequency_days": 14,
    "min_amount": 25.00
  }
}
```

---

## Smart Reminders

The app implements intelligent reminder logic based on user payment patterns:

### Reminder Types

| Type | Trigger | Content |
|------|---------|---------|
| Regular Reminder | Based on frequency_days | "You owe $X to Y people" |
| Gentle Nudge | Debt outstanding > 30 days | "Friendly reminder about your balance" |
| Celebration | All debts settled | "Congrats! You're all settled up" |

### Smart Features
- No reminders on weekends (unless configured)
- Batch reminders for multiple debts
- Learn optimal reminder times from user engagement
- Stop reminders after 3 ignored (mark as acknowledged)

---

## Unsubscribe Flow

### Email Unsubscribe Link
Every email contains an unsubscribe link that:
1. Opens a web page (no login required)
2. Uses signed token to identify user
3. Allows disabling specific notification or all notifications

### Technical Requirements

**Unsubscribe via Token**
```
GET /api/v1/notifications/unsubscribe?token=xxx&type=expense_added
```

**Response**
```json
HTTP 200 OK
{
  "message": "You have been unsubscribed from expense_added notifications",
  "resubscribe_url": "/settings/notifications"
}
```

---

## Data Model

### NotificationPreferences Schema

```python
class NotificationPreferences:
    user_id: UUID
    email_enabled: bool = True

    # Digest settings (stored as JSONB)
    digest_frequency: str = "off"  # off, daily, weekly
    digest_day: str = "monday"  # For weekly
    digest_time: str = "09:00"
    digest_timezone: str = "UTC"

    # Individual notifications (stored as JSONB)
    notifications: dict = {
        "expense_added": True,
        "expense_edited": True,
        # ... all notification types
    }

    # Reminder settings (stored as JSONB)
    reminder_enabled: bool = True
    reminder_frequency_days: int = 7
    reminder_min_amount: Decimal = 10.00

    created_at: datetime
    updated_at: datetime
```

---

## Acceptance Criteria

### View Preferences
- [ ] User can view all current notification settings
- [ ] Default values shown for new users
- [ ] Digest settings are displayed correctly

### Update Preferences
- [ ] User can toggle individual notifications
- [ ] User can change digest frequency
- [ ] User can set digest time and timezone
- [ ] Partial updates work correctly

### Disable All
- [ ] User can disable all email notifications
- [ ] No emails sent when disabled
- [ ] User can re-enable easily

### Reminders
- [ ] User can enable/disable reminders
- [ ] User can set reminder frequency
- [ ] User can set minimum amount threshold
- [ ] Smart reminders respect user patterns

### Unsubscribe
- [ ] Every email has unsubscribe link
- [ ] Unsubscribe works without login
- [ ] User can resubscribe from settings
- [ ] Unsubscribe is immediate
