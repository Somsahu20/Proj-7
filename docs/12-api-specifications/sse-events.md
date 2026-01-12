# SSE Events

## Overview

Server-Sent Events provide real-time updates to connected clients.

---

## Connection

### Endpoint
```
GET /api/v1/notifications/stream
Authorization: Bearer <access_token>
Accept: text/event-stream
```

### Connection Lifecycle
1. Client connects with auth token
2. Server validates and registers connection
3. Server sends heartbeat every 30 seconds
4. Client reconnects automatically on disconnect

---

## Event Format

```
event: <event_type>
data: <json_payload>
id: <event_id>

```

---

## Event Types

### notification:new

New notification for the user.

```
event: notification:new
data: {
  "id": "uuid",
  "type": "expense_added",
  "title": "New expense",
  "body": "John added 'Dinner' ($120)",
  "action_url": "/groups/uuid/expenses/uuid",
  "created_at": "2026-01-11T20:00:00Z"
}
```

---

### expense:created

New expense in a group.

```
event: expense:created
data: {
  "group_id": "uuid",
  "expense": {
    "id": "uuid",
    "description": "Dinner",
    "amount": 120.00,
    "payer": {...}
  }
}
```

---

### expense:updated

Expense modified.

```
event: expense:updated
data: {
  "group_id": "uuid",
  "expense_id": "uuid",
  "changes": {
    "amount": {"from": 100, "to": 120}
  }
}
```

---

### expense:deleted

Expense removed.

```
event: expense:deleted
data: {
  "group_id": "uuid",
  "expense_id": "uuid"
}
```

---

### payment:recorded

Payment recorded, awaiting confirmation.

```
event: payment:recorded
data: {
  "group_id": "uuid",
  "payment": {
    "id": "uuid",
    "payer": {...},
    "receiver": {...},
    "amount": 50.00
  }
}
```

---

### payment:confirmed

Payment confirmed by receiver.

```
event: payment:confirmed
data: {
  "group_id": "uuid",
  "payment_id": "uuid",
  "confirmed_at": "2026-01-11T16:00:00Z"
}
```

---

### balance:updated

User's balance changed.

```
event: balance:updated
data: {
  "group_id": "uuid",
  "user_id": "uuid",
  "old_balance": -95.50,
  "new_balance": -125.50,
  "change": -30.00
}
```

---

### member:joined

New member joined group.

```
event: member:joined
data: {
  "group_id": "uuid",
  "member": {
    "id": "uuid",
    "name": "Alice Brown"
  }
}
```

---

### ping

Heartbeat to keep connection alive.

```
event: ping
data: {"timestamp": "2026-01-11T20:00:00Z"}
```

---

## Client Implementation

```javascript
const eventSource = new EventSource('/api/v1/notifications/stream', {
  headers: { 'Authorization': `Bearer ${token}` }
});

eventSource.addEventListener('notification:new', (e) => {
  const notification = JSON.parse(e.data);
  showToast(notification);
});

eventSource.addEventListener('expense:created', (e) => {
  const data = JSON.parse(e.data);
  if (currentGroupId === data.group_id) {
    refreshExpenseList();
  }
});

eventSource.onerror = () => {
  // Auto-reconnect handled by EventSource
};
```

---

## Filtering

Events are filtered per-user:
- Only events for groups user is member of
- Only relevant notifications
- Payment events only for payer/receiver
