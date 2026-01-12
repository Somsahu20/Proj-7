# Notification Endpoints

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /notifications | List notifications |
| GET | /notifications/unread-count | Get unread count |
| POST | /notifications/:id/read | Mark as read |
| POST | /notifications/read-all | Mark all as read |
| DELETE | /notifications/:id | Delete notification |
| GET | /notifications/stream | SSE stream |

---

## GET /notifications

### Query Parameters
- page, limit
- is_read: boolean
- type: string

### Response 200
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "expense_added",
      "title": "New expense",
      "body": "John added 'Dinner' ($120)",
      "action_url": "/groups/uuid/expenses/uuid",
      "is_read": false,
      "created_at": "2026-01-11T20:00:00Z"
    }
  ],
  "unread_count": 5,
  "pagination": {...}
}
```

---

## GET /notifications/unread-count

### Response 200
```json
{
  "unread_count": 5,
  "by_type": {
    "expense_added": 2,
    "payment_received": 1
  }
}
```

---

## POST /notifications/:id/read

### Response 200
```json
{
  "id": "uuid",
  "is_read": true
}
```

---

## POST /notifications/read-all

### Response 200
```json
{
  "marked_read": 15
}
```

---

## DELETE /notifications/:id

### Response 200
```json
{
  "message": "Notification deleted"
}
```

---

## GET /notifications/stream

### Headers
```
Accept: text/event-stream
Authorization: Bearer <token>
```

### Response
SSE stream with events. See [SSE Events](./sse-events.md) for details.
