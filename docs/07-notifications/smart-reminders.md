# Smart Reminders

## Overview

The app sends intelligent reminders based on user behavior, payment patterns, and configurable preferences.

---

## Reminder Types

### Balance Reminders

| Type | Trigger | Content |
|------|---------|---------|
| Regular | Scheduled (every X days) | "You owe $X to Y people" |
| Gentle Nudge | Debt > 30 days old | "Friendly reminder about your balance" |
| Urgent | Debt > 60 days old | "Don't forget to settle your balance" |

### Payment Reminders

| Type | Trigger | Content |
|------|---------|---------|
| Pending Confirmation | Payment awaiting 24+ hours | "Please confirm payment from X" |
| Stale Payment | Payment pending 7+ days | "X is waiting for your confirmation" |

### Celebration Notifications

| Type | Trigger | Content |
|------|---------|---------|
| Debt Cleared | User balance reaches $0 | "Congrats! You're all settled!" |
| Group Settled | All group balances = $0 | "Group is fully settled!" |
| Streak | 3+ on-time settlements | "You're on a payment streak!" |

---

## Reminder Configuration

### User Settings

**Request**
```
GET /api/v1/users/me/notification-preferences
```

**Response (Reminder Section)**
```json
{
  "reminder_settings": {
    "enabled": true,
    "frequency_days": 7,
    "min_amount": 10.00,
    "preferred_time": "09:00",
    "timezone": "America/New_York",
    "weekend_reminders": false,
    "gentle_nudges": true
  }
}
```

### Update Settings

**Request**
```json
PATCH /api/v1/users/me/notification-preferences
{
  "reminder_settings": {
    "frequency_days": 14,
    "min_amount": 25.00,
    "weekend_reminders": true
  }
}
```

---

## Smart Timing

### Learn from Behavior

The system tracks when users typically:
- Open emails
- Confirm payments
- Add expenses

And adjusts reminder timing accordingly.

### Optimal Send Time

```python
def get_optimal_send_time(user_id: str) -> time:
    """
    Determine the best time to send reminders based on user engagement.
    """
    # Get user's engagement history
    engagement_hours = get_engagement_hours(user_id)

    if engagement_hours:
        # Find peak engagement hour
        peak_hour = max(engagement_hours, key=engagement_hours.get)
        return time(hour=peak_hour)
    else:
        # Default to user's preferred time or 9 AM
        return user.preferred_time or time(hour=9)
```

---

## Reminder Logic

### Should Send Reminder

```python
def should_send_reminder(user: User, last_reminder: datetime) -> bool:
    settings = user.reminder_settings

    # Check if reminders are enabled
    if not settings.enabled:
        return False

    # Check minimum amount threshold
    if abs(user.total_balance) < settings.min_amount:
        return False

    # Check frequency
    days_since_last = (now() - last_reminder).days
    if days_since_last < settings.frequency_days:
        return False

    # Check weekend preference
    if not settings.weekend_reminders and is_weekend():
        return False

    # Check if user has acknowledged (3+ ignored reminders)
    if user.ignored_reminders >= 3:
        return False

    return True
```

---

## Gentle Nudges

### What are Gentle Nudges?

Friendly, non-pushy reminders for long-standing debts.

### Nudge Strategy

| Debt Age | Nudge Type | Frequency |
|----------|------------|-----------|
| 30-45 days | Friendly | Once |
| 45-60 days | Encouraging | Once |
| 60+ days | Supportive | Monthly |

### Nudge Examples

**30 Days (Friendly)**
```
Hey {name}! Just a gentle reminder - you have a $X balance in {group}.
No rush, but wanted to keep you in the loop! 💙
```

**45 Days (Encouraging)**
```
Hey {name}, checking in! You've got $X outstanding in {group}.
Settling up keeps friendships smooth! ✨
```

**60+ Days (Supportive)**
```
Hi {name}, hope you're doing well! This is a monthly check-in about
your $X balance in {group}. Let us know if you need any help! 🤝
```

---

## Celebration Notifications

### Debt Cleared

**Trigger**: User's balance in a group reaches $0

**Email**:
```
🎉 Congratulations {name}!

You've cleared all your debts in "{group_name}"!

Summary:
- Total settled: ${total_amount}
- Payments made: {payment_count}
- Duration: {days} days

Keep up the great work!

[View Group]
```

### Group Settled

**Trigger**: All members have $0 balance

**Email to all members**:
```
🎊 "{group_name}" is fully settled!

Great teamwork, everyone! All debts have been paid.

Group Statistics:
- Total expenses: ${total}
- Members: {count}
- Duration: {days} days

Would you like to archive this group?

[Archive Group] [Keep Active]
```

### Settlement Streak

**Trigger**: User settles on time 3+ times in a row

**Email**:
```
🔥 You're on fire, {name}!

You've settled your debts on time 3 times in a row.
Your reliability score is looking great!

Keep the streak going!

[View Your Profile]
```

---

## Reminder API

### Get Pending Reminders

**Request**
```
GET /api/v1/users/me/reminders/pending
Authorization: Bearer <access_token>
```

**Response**
```json
{
  "pending_reminders": [
    {
      "type": "balance_reminder",
      "group_id": "uuid",
      "group_name": "Trip to Paris",
      "amount": 125.50,
      "scheduled_for": "2026-01-12T09:00:00Z"
    }
  ]
}
```

### Snooze Reminder

**Request**
```
POST /api/v1/users/me/reminders/{reminder_id}/snooze
{
  "duration_days": 7
}
```

**Response**
```json
{
  "message": "Reminder snoozed for 7 days",
  "next_reminder": "2026-01-18T09:00:00Z"
}
```

### Acknowledge (Stop Reminders)

**Request**
```
POST /api/v1/users/me/reminders/{reminder_id}/acknowledge
{
  "reason": "Will pay at end of month"
}
```

**Response**
```json
{
  "message": "Reminder acknowledged. We won't remind you again for this balance.",
  "note": "You can always settle up from the app anytime."
}
```

---

## Reminder Schedule

### Background Job

```python
# Run every hour
@scheduler.scheduled_job('interval', hours=1)
def process_reminders():
    # Get users due for reminders
    users = get_users_due_for_reminder()

    for user in users:
        # Check optimal send time
        if is_optimal_time(user):
            send_reminder(user)
            update_last_reminder(user)
```

---

## Acceptance Criteria

### Balance Reminders
- [ ] Sent based on frequency setting
- [ ] Respects minimum amount
- [ ] Respects weekend preference
- [ ] Optimal timing applied

### Gentle Nudges
- [ ] Triggered for old debts
- [ ] Friendly, non-pushy tone
- [ ] Progressive messaging

### Celebrations
- [ ] Sent when balance cleared
- [ ] Sent when group settled
- [ ] Streak tracking works

### User Control
- [ ] Can enable/disable
- [ ] Can snooze
- [ ] Can acknowledge to stop
- [ ] Settings respected
