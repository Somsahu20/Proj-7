# Group Settings

## Overview

Group admins can modify group settings, view group statistics, and delete groups when all balances are settled.

---

## View Group Details

### User Story
> As a group member, I want to view complete group details and settings.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "id": "uuid",
  "name": "Trip to Paris",
  "description": "Our summer vacation to Paris 2026",
  "category": "trip",
  "image_url": "/uploads/groups/uuid/image.jpg",
  "created_by": {
    "id": "user-uuid",
    "name": "John Doe"
  },
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-10T15:30:00Z",
  "member_count": 4,
  "expense_count": 25,
  "total_expenses": 1250.50,
  "is_settled": false,
  "my_role": "admin",
  "my_balance": -125.25
}
```

---

## Edit Group Details

### User Story
> As a group admin, I want to edit group details to keep them up to date.

### Editable Fields

| Field | Validation |
|-------|------------|
| name | 3-100 chars |
| description | Max 500 chars |
| category | Valid category enum |

### Technical Requirements

**Request**
```json
PATCH /api/v1/groups/{group_id}
Authorization: Bearer <access_token>
{
  "name": "Paris Trip 2026",
  "description": "Updated description",
  "category": "trip"
}
```

**Response**
```json
HTTP 200 OK
{
  "id": "uuid",
  "name": "Paris Trip 2026",
  "description": "Updated description",
  "category": "trip",
  "updated_at": "2026-01-11T10:00:00Z"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not admin | `{"detail": "Only admins can edit group settings"}` |
| 400 | Invalid data | `{"detail": "Group name must be at least 3 characters"}` |

### Side Effects
- All members notified of changes (if enabled)
- Activity logged

---

## Group Statistics

### User Story
> As a group member, I want to see statistics about the group's expenses and payments.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/statistics
Authorization: Bearer <access_token>
Query Parameters:
  - period: string (all_time | this_month | last_month | custom)
  - start_date: date (for custom period)
  - end_date: date (for custom period)
```

**Response**
```json
HTTP 200 OK
{
  "period": {
    "start": "2026-01-01",
    "end": "2026-01-11"
  },
  "summary": {
    "total_expenses": 1250.50,
    "expense_count": 25,
    "total_payments": 500.00,
    "payment_count": 8,
    "outstanding_balance": 750.50
  },
  "by_category": [
    {
      "category": "Food & Drinks",
      "amount": 450.00,
      "count": 12,
      "percentage": 36.0
    },
    {
      "category": "Transport",
      "amount": 300.00,
      "count": 5,
      "percentage": 24.0
    },
    {
      "category": "Accommodation",
      "amount": 350.00,
      "count": 3,
      "percentage": 28.0
    },
    {
      "category": "Activities",
      "amount": 150.50,
      "count": 5,
      "percentage": 12.0
    }
  ],
  "by_member": [
    {
      "member_id": "uuid-1",
      "name": "John Doe",
      "paid": 600.00,
      "owes": 312.50,
      "balance": 287.50
    },
    {
      "member_id": "uuid-2",
      "name": "Jane Smith",
      "paid": 400.00,
      "owes": 312.50,
      "balance": 87.50
    },
    {
      "member_id": "uuid-3",
      "name": "Bob Wilson",
      "paid": 250.50,
      "owes": 312.50,
      "balance": -62.00
    },
    {
      "member_id": "uuid-4",
      "name": "Alice Brown",
      "paid": 0.00,
      "owes": 313.00,
      "balance": -313.00
    }
  ],
  "top_expenses": [
    {
      "id": "expense-uuid",
      "description": "Hotel booking",
      "amount": 350.00,
      "date": "2026-01-05"
    },
    {
      "id": "expense-uuid",
      "description": "Train tickets",
      "amount": 200.00,
      "date": "2026-01-03"
    }
  ],
  "monthly_trend": [
    {
      "month": "2026-01",
      "total": 1250.50,
      "count": 25
    }
  ]
}
```

---

## Group Activity Log

### User Story
> As a group member, I want to see a history of all activities in the group.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/activity
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20, max: 50)
  - type: string (optional, filter by activity type)
```

**Response**
```json
HTTP 200 OK
{
  "activities": [
    {
      "id": "activity-uuid",
      "type": "expense_added",
      "actor": {
        "id": "user-uuid",
        "name": "John Doe"
      },
      "data": {
        "expense_id": "expense-uuid",
        "description": "Dinner at restaurant",
        "amount": 80.00
      },
      "created_at": "2026-01-11T20:00:00Z"
    },
    {
      "id": "activity-uuid",
      "type": "member_joined",
      "actor": {
        "id": "user-uuid",
        "name": "Alice Brown"
      },
      "data": {},
      "created_at": "2026-01-10T14:00:00Z"
    },
    {
      "id": "activity-uuid",
      "type": "payment_confirmed",
      "actor": {
        "id": "user-uuid",
        "name": "Jane Smith"
      },
      "data": {
        "payment_id": "payment-uuid",
        "from": "Bob Wilson",
        "amount": 50.00
      },
      "created_at": "2026-01-09T10:00:00Z"
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

### Activity Types

| Type | Description |
|------|-------------|
| `group_created` | Group was created |
| `group_updated` | Group settings changed |
| `member_joined` | New member joined |
| `member_left` | Member left the group |
| `member_removed` | Member was removed |
| `role_changed` | Member role was updated |
| `expense_added` | New expense added |
| `expense_updated` | Expense was modified |
| `expense_deleted` | Expense was deleted |
| `payment_recorded` | Payment was recorded |
| `payment_confirmed` | Payment was confirmed |
| `payment_rejected` | Payment was rejected |

---

## Delete Group

### User Story
> As a group admin, I want to delete a group when it's no longer needed.

### Prerequisites
- User must be admin
- All balances must be settled (everyone's balance = 0)
- OR admin confirms deletion with outstanding balances

### Technical Requirements

**Check if Deletable**
```
GET /api/v1/groups/{group_id}/can-delete
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "can_delete": false,
  "reason": "Outstanding balances exist",
  "outstanding_balances": [
    {
      "member": "Alice Brown",
      "balance": -313.00
    },
    {
      "member": "Bob Wilson",
      "balance": -62.00
    }
  ]
}
```

**Delete Group**
```json
DELETE /api/v1/groups/{group_id}
Authorization: Bearer <access_token>
{
  "confirmation": "DELETE",
  "force": false
}
```

| Parameter | Description |
|-----------|-------------|
| confirmation | Must be "DELETE" to confirm |
| force | If true, delete despite outstanding balances |

**Response (Success)**
```json
HTTP 200 OK
{
  "message": "Group deleted successfully"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not admin | `{"detail": "Only admins can delete groups"}` |
| 400 | Wrong confirmation | `{"detail": "Please type DELETE to confirm"}` |
| 400 | Balances exist, force=false | `{"detail": "Group has outstanding balances"}` |

### Side Effects
- All members notified
- Group data marked as deleted (soft delete)
- Data retained for 30 days, then permanently deleted
- Expenses and payments archived for user history

---

## Archive Group

### User Story
> As a group admin, I want to archive a completed group to keep it for reference without cluttering my active groups.

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/archive
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Group archived",
  "archived_at": "2026-01-11T10:00:00Z"
}
```

### Archived Group Behavior
- Read-only (no new expenses or payments)
- Appears in "Archived" section
- Can be unarchived by admin

**Unarchive**
```json
POST /api/v1/groups/{group_id}/unarchive
Authorization: Bearer <access_token>
```

---

## List User's Groups

### User Story
> As a user, I want to see all groups I'm a member of.

### Technical Requirements

**Request**
```
GET /api/v1/groups
Authorization: Bearer <access_token>
Query Parameters:
  - status: string (active | archived | all)
  - page: int
  - limit: int
```

**Response**
```json
HTTP 200 OK
{
  "groups": [
    {
      "id": "uuid",
      "name": "Trip to Paris",
      "category": "trip",
      "image_url": "/uploads/groups/uuid/image.jpg",
      "member_count": 4,
      "my_balance": -125.25,
      "last_activity": "2026-01-11T10:00:00Z",
      "is_archived": false
    },
    {
      "id": "uuid",
      "name": "Apartment 4B",
      "category": "apartment",
      "image_url": null,
      "member_count": 3,
      "my_balance": 50.00,
      "last_activity": "2026-01-10T15:00:00Z",
      "is_archived": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "pages": 1
  }
}
```

---

## Acceptance Criteria

### View Group
- [ ] All group details are displayed
- [ ] Member count is accurate
- [ ] User's role is shown
- [ ] User's balance is displayed

### Edit Group
- [ ] Admin can edit name
- [ ] Admin can edit description
- [ ] Admin can change category
- [ ] Non-admin cannot edit

### Statistics
- [ ] Summary totals are accurate
- [ ] Category breakdown is correct
- [ ] Per-member statistics are shown
- [ ] Date filtering works

### Activity Log
- [ ] All activities are logged
- [ ] Pagination works
- [ ] Filtering by type works
- [ ] Timestamps are correct

### Delete Group
- [ ] Only admin can delete
- [ ] Must confirm with "DELETE"
- [ ] Warning shown for outstanding balances
- [ ] Force delete option works
- [ ] Members are notified

### Archive Group
- [ ] Admin can archive
- [ ] Archived groups are read-only
- [ ] Admin can unarchive
- [ ] Archived groups appear separately
