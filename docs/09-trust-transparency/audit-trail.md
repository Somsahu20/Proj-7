# Audit Trail

## Overview

Every action in the app is logged to provide a complete, immutable record of all activities.

---

## Tracked Events

### Expense Events
| Event | Data Logged |
|-------|-------------|
| Created | Full expense data, splits |
| Updated | Before/after values |
| Deleted | Full expense data at deletion |

### Payment Events
| Event | Data Logged |
|-------|-------------|
| Recorded | Amount, parties, proof |
| Confirmed | Confirmation time, confirmer |
| Rejected | Reason, rejecter |
| Cancelled | Reason, canceller |

### Group Events
| Event | Data Logged |
|-------|-------------|
| Created | Creator, initial settings |
| Updated | Changed fields |
| Member added | Inviter, invitee |
| Member removed | Remover, removee, reason |

---

## View Audit Log

**Request**
```
GET /api/v1/groups/{group_id}/audit-log
Authorization: Bearer <access_token>
Query Parameters:
  - page: int
  - limit: int
  - entity_type: string (expense | payment | group | member)
  - entity_id: uuid
  - actor_id: uuid
  - start_date: date
  - end_date: date
```

**Response**
```json
HTTP 200 OK
{
  "entries": [
    {
      "id": "audit-uuid",
      "timestamp": "2026-01-11T20:00:00Z",
      "actor": {"id": "uuid", "name": "John Doe"},
      "action": "expense.updated",
      "entity_type": "expense",
      "entity_id": "expense-uuid",
      "changes": {
        "amount": {"from": 100.00, "to": 120.00},
        "description": {"from": "Dinner", "to": "Dinner at restaurant"}
      },
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "pagination": {...}
}
```

---

## Expense History

**Request**
```
GET /api/v1/groups/{group_id}/expenses/{expense_id}/history
```

**Response**
```json
{
  "history": [
    {
      "version": 1,
      "timestamp": "2026-01-11T18:00:00Z",
      "actor": {"name": "John Doe"},
      "action": "created",
      "data": {"amount": 100.00, "description": "Dinner"}
    },
    {
      "version": 2,
      "timestamp": "2026-01-11T20:00:00Z",
      "actor": {"name": "John Doe"},
      "action": "updated",
      "changes": {"amount": {"from": 100.00, "to": 120.00}}
    }
  ]
}
```

---

## Data Retention

| Data Type | Retention |
|-----------|-----------|
| Active groups | Indefinite |
| Deleted groups | 30 days |
| Audit logs | 1 year |
| Deleted user data | 14 days grace, then purged |

---

## Acceptance Criteria

- [ ] All actions are logged
- [ ] Changes show before/after
- [ ] Filtering works correctly
- [ ] Immutable (cannot be modified)
- [ ] Accessible to group members
