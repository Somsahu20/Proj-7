# Activity Feed

## Overview

The activity feed shows a real-time stream of all group activities, updated via Server-Sent Events.

---

## Activity Types

| Type | Description |
|------|-------------|
| `expense_added` | New expense created |
| `expense_updated` | Expense modified |
| `expense_deleted` | Expense removed |
| `payment_recorded` | Payment recorded |
| `payment_confirmed` | Payment confirmed |
| `payment_rejected` | Payment rejected |
| `member_joined` | New member |
| `member_left` | Member left |
| `member_removed` | Member removed |
| `comment_added` | New comment |
| `group_updated` | Settings changed |

---

## Get Activity Feed

**Request**
```
GET /api/v1/groups/{group_id}/activity
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20)
  - type: string (optional filter)
  - actor_id: uuid (optional filter)
  - start_date: date (optional)
  - end_date: date (optional)
```

**Response**
```json
HTTP 200 OK
{
  "activities": [
    {
      "id": "activity-uuid-1",
      "type": "expense_added",
      "actor": {
        "id": "user-uuid",
        "name": "John Doe",
        "profile_picture": "/uploads/profiles/uuid/photo.jpg"
      },
      "data": {
        "expense_id": "expense-uuid",
        "description": "Dinner at restaurant",
        "amount": 120.00
      },
      "message": "John added 'Dinner at restaurant' ($120.00)",
      "created_at": "2026-01-11T20:00:00Z"
    },
    {
      "id": "activity-uuid-2",
      "type": "payment_confirmed",
      "actor": {
        "id": "user-uuid",
        "name": "Jane Smith"
      },
      "data": {
        "payment_id": "payment-uuid",
        "payer": "Bob Wilson",
        "amount": 50.00
      },
      "message": "Jane confirmed $50.00 payment from Bob",
      "created_at": "2026-01-11T18:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

## Real-time Stream (SSE)

### Connection

**Request**
```
GET /api/v1/groups/{group_id}/activity/stream
Authorization: Bearer <access_token>
Accept: text/event-stream
```

### Events

```
event: activity
data: {
  "id": "activity-uuid",
  "type": "expense_added",
  "actor": {"id": "uuid", "name": "John Doe"},
  "data": {"expense_id": "uuid", "description": "Coffee", "amount": 15.00},
  "message": "John added 'Coffee' ($15.00)",
  "created_at": "2026-01-11T20:30:00Z"
}

event: activity
data: {
  "id": "activity-uuid",
  "type": "payment_recorded",
  ...
}
```

### Heartbeat

```
event: ping
data: {"timestamp": "2026-01-11T20:30:00Z"}
```

---

## Activity Messages

| Type | Message Template |
|------|-----------------|
| `expense_added` | {actor} added '{description}' (${amount}) |
| `expense_updated` | {actor} updated '{description}' |
| `expense_deleted` | {actor} deleted '{description}' |
| `payment_recorded` | {actor} recorded ${amount} payment to {receiver} |
| `payment_confirmed` | {actor} confirmed ${amount} payment from {payer} |
| `member_joined` | {actor} joined the group |
| `member_left` | {actor} left the group |
| `comment_added` | {actor} commented on '{expense}' |

---

## Acceptance Criteria

### Feed
- [ ] Shows all activity types
- [ ] Pagination works
- [ ] Filters work
- [ ] Newest first

### Real-time
- [ ] SSE connection established
- [ ] Events received in real-time
- [ ] Automatic reconnection
- [ ] Heartbeat keeps connection alive
