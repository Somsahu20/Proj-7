# Approval Workflow

## Overview

Groups can optionally enable expense approval, requiring designated approvers to approve expenses before they affect balances.

---

## Enable Approval

### Group Setting

**Request**
```json
PATCH /api/v1/groups/{group_id}/settings
Authorization: Bearer <access_token>
{
  "expense_approval": {
    "enabled": true,
    "threshold": 50.00,
    "approvers": ["admin", "user-uuid-1"]
  }
}
```

| Setting | Description |
|---------|-------------|
| enabled | Turn approval on/off |
| threshold | Only require for expenses >= threshold |
| approvers | Who can approve ("admin" or specific users) |

---

## Expense States

```
┌─────────┐ create  ┌─────────┐
│         │────────▶│ PENDING │
└─────────┘         └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               │               ▼
   ┌───────────┐         │         ┌───────────┐
   │ APPROVED  │         │         │ REJECTED  │
   └───────────┘         │         └───────────┘
                         │
                  (below threshold)
                         │
                         ▼
                   ┌───────────┐
                   │ APPROVED  │
                   │  (auto)   │
                   └───────────┘
```

---

## Pending Expenses

**Request**
```
GET /api/v1/groups/{group_id}/expenses/pending-approval
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "pending_expenses": [
    {
      "id": "expense-uuid",
      "description": "Team dinner",
      "amount": 200.00,
      "created_by": {"id": "uuid", "name": "John Doe"},
      "created_at": "2026-01-11T19:00:00Z",
      "can_approve": true
    }
  ],
  "total": 1
}
```

---

## Approve Expense

**Request**
```
POST /api/v1/groups/{group_id}/expenses/{expense_id}/approve
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "id": "expense-uuid",
  "status": "approved",
  "approved_by": {"id": "uuid", "name": "Jane Smith"},
  "approved_at": "2026-01-11T20:00:00Z",
  "message": "Expense approved. Balances have been updated."
}
```

---

## Reject Expense

**Request**
```json
POST /api/v1/groups/{group_id}/expenses/{expense_id}/reject
Authorization: Bearer <access_token>
{
  "reason": "Please split this into separate expenses"
}
```

**Response**
```json
HTTP 200 OK
{
  "id": "expense-uuid",
  "status": "rejected",
  "rejected_by": {"id": "uuid", "name": "Jane Smith"},
  "rejected_at": "2026-01-11T20:00:00Z",
  "reason": "Please split this into separate expenses"
}
```

Creator is notified and can edit and resubmit.

---

## Acceptance Criteria

### Configuration
- [ ] Admin can enable/disable
- [ ] Threshold is respected
- [ ] Approvers are configurable

### Workflow
- [ ] Expenses below threshold auto-approved
- [ ] Above threshold requires approval
- [ ] Approvers can approve/reject
- [ ] Creator notified of decision

### Balances
- [ ] Pending expenses don't affect balance
- [ ] Approved expenses update balance
- [ ] Rejected expenses don't affect balance
