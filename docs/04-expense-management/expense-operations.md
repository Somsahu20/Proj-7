# Expense Operations

## Overview

This document covers viewing, filtering, editing, and deleting expenses, as well as receipt management.

---

## View Expense List

### User Story
> As a group member, I want to see all expenses in the group.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/expenses
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20, max: 50)
  - sort: string (date_desc | date_asc | amount_desc | amount_asc)
```

**Response**
```json
HTTP 200 OK
{
  "expenses": [
    {
      "id": "expense-uuid-1",
      "description": "Dinner at Italian restaurant",
      "amount": 120.00,
      "date": "2026-01-11",
      "payer": {
        "id": "user-uuid",
        "name": "John Doe",
        "profile_picture": "/uploads/profiles/uuid/photo.jpg"
      },
      "split_type": "equal",
      "participant_count": 4,
      "category": "Food & Drinks",
      "category_icon": "🍕",
      "has_receipt": true,
      "my_share": 30.00,
      "i_paid": false,
      "created_at": "2026-01-11T20:00:00Z"
    },
    {
      "id": "expense-uuid-2",
      "description": "Train tickets",
      "amount": 80.00,
      "date": "2026-01-10",
      "payer": {
        "id": "user-uuid",
        "name": "Jane Smith"
      },
      "split_type": "equal",
      "participant_count": 4,
      "category": "Transport",
      "category_icon": "🚗",
      "has_receipt": false,
      "my_share": 20.00,
      "i_paid": false,
      "created_at": "2026-01-10T14:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 25,
    "pages": 2
  },
  "summary": {
    "total_expenses": 1250.50,
    "expense_count": 25
  }
}
```

---

## View Expense Details

### User Story
> As a group member, I want to see full details of a specific expense.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/expenses/{expense_id}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "id": "expense-uuid",
  "description": "Dinner at Italian restaurant",
  "amount": 120.00,
  "date": "2026-01-11",
  "payer": {
    "id": "user-uuid-1",
    "name": "John Doe",
    "profile_picture": "/uploads/profiles/uuid/photo.jpg"
  },
  "split_type": "equal",
  "splits": [
    {
      "user_id": "user-uuid-1",
      "name": "John Doe",
      "amount": 30.00,
      "is_payer": true,
      "is_settled": false
    },
    {
      "user_id": "user-uuid-2",
      "name": "Jane Smith",
      "amount": 30.00,
      "is_payer": false,
      "is_settled": false
    },
    {
      "user_id": "user-uuid-3",
      "name": "Bob Wilson",
      "amount": 30.00,
      "is_payer": false,
      "is_settled": true
    },
    {
      "user_id": "user-uuid-4",
      "name": "Alice Brown",
      "amount": 30.00,
      "is_payer": false,
      "is_settled": false
    }
  ],
  "category": "Food & Drinks",
  "notes": "Great pizza place near the hotel",
  "receipt_url": "/uploads/expenses/uuid/receipt.jpg",
  "created_by": {
    "id": "user-uuid-1",
    "name": "John Doe"
  },
  "created_at": "2026-01-11T20:00:00Z",
  "updated_at": null,
  "comments_count": 2,
  "reactions": {
    "👍": 2,
    "😋": 1
  },
  "can_edit": true,
  "can_delete": true
}
```

---

## Filter Expenses

### Available Filters

| Filter | Type | Description |
|--------|------|-------------|
| category | string | Filter by category name |
| payer_id | uuid | Filter by who paid |
| participant_id | uuid | Filter by participant |
| date_from | date | Expenses on or after this date |
| date_to | date | Expenses on or before this date |
| amount_min | decimal | Minimum amount |
| amount_max | decimal | Maximum amount |
| has_receipt | boolean | Has receipt attached |
| search | string | Search in description |

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/expenses
  ?category=Transport
  &payer_id=user-uuid
  &date_from=2026-01-01
  &date_to=2026-01-31
  &amount_min=10
  &amount_max=100
  &search=taxi
Authorization: Bearer <access_token>
```

**Response**
Same as list response, but filtered.

### Filter Presets

| Preset | Filters Applied |
|--------|-----------------|
| My Expenses | `payer_id=current_user` |
| I Owe | `participant_id=current_user` AND `payer_id!=current_user` |
| This Month | `date_from=first_of_month` AND `date_to=today` |
| Unsettled | `is_settled=false` |

---

## Edit Expense

### User Story
> As the expense creator or group admin, I want to edit an expense to correct mistakes.

### Permissions

| Role | Can Edit Own | Can Edit Others |
|------|--------------|-----------------|
| Admin | ✅ | ✅ |
| Member | ✅ | ❌ |

### Editable Fields

| Field | Editable | Notes |
|-------|----------|-------|
| description | ✅ | |
| amount | ✅ | Recalculates splits |
| date | ✅ | Cannot be future |
| payer_id | ✅ | Must be member |
| participants | ✅ | Must be members |
| split_type | ✅ | |
| splits | ✅ | For unequal/shares/percentage |
| category | ✅ | |
| notes | ✅ | |

### Technical Requirements

**Request**
```json
PATCH /api/v1/groups/{group_id}/expenses/{expense_id}
Authorization: Bearer <access_token>
{
  "description": "Dinner at French restaurant",
  "amount": 130.00,
  "category": "Food & Drinks"
}
```

**Response**
```json
HTTP 200 OK
{
  "id": "expense-uuid",
  "description": "Dinner at French restaurant",
  "amount": 130.00,
  "...": "...",
  "updated_at": "2026-01-11T22:00:00Z",
  "updated_by": {
    "id": "user-uuid",
    "name": "John Doe"
  }
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not creator or admin | `{"detail": "You don't have permission to edit this expense"}` |
| 400 | Invalid data | `{"detail": "Amount must be greater than 0"}` |

### Side Effects
- Balances recalculated for all affected members
- Edit history recorded
- Participants notified of changes
- SSE broadcast

---

## Delete Expense

### User Story
> As the expense creator or group admin, I want to delete an expense that was added by mistake.

### Permissions

| Role | Can Delete Own | Can Delete Others |
|------|----------------|-------------------|
| Admin | ✅ | ✅ |
| Member | ✅ | ❌ |

### Technical Requirements

**Request**
```
DELETE /api/v1/groups/{group_id}/expenses/{expense_id}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Expense deleted",
  "balance_changes": [
    {"user_id": "uuid-1", "change": -30.00},
    {"user_id": "uuid-2", "change": +30.00}
  ]
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not creator or admin | `{"detail": "You don't have permission to delete this expense"}` |

### Side Effects
- Balances recalculated
- Deletion logged in activity
- Participants notified
- SSE broadcast

### Soft Delete
- Expense marked as deleted, not permanently removed
- Can be restored by admin within 30 days
- After 30 days, permanently deleted

---

## Receipt Management

### View Receipt

**Request**
```
GET /api/v1/groups/{group_id}/expenses/{expense_id}/receipt
Authorization: Bearer <access_token>
```

**Response**
Redirect to file or return file directly.

### Add Receipt to Existing Expense

**Request**
```
POST /api/v1/groups/{group_id}/expenses/{expense_id}/receipt
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image/pdf>
```

**Response**
```json
HTTP 200 OK
{
  "receipt_url": "/uploads/expenses/uuid/receipt.jpg",
  "message": "Receipt uploaded"
}
```

### Replace Receipt

**Request**
```
PUT /api/v1/groups/{group_id}/expenses/{expense_id}/receipt
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image/pdf>
```

**Response**
```json
HTTP 200 OK
{
  "receipt_url": "/uploads/expenses/uuid/receipt_new.jpg",
  "message": "Receipt replaced"
}
```

### Delete Receipt

**Request**
```
DELETE /api/v1/groups/{group_id}/expenses/{expense_id}/receipt
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Receipt removed"
}
```

---

## Expense History

### User Story
> As a group member, I want to see the edit history of an expense.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/expenses/{expense_id}/history
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "history": [
    {
      "action": "created",
      "actor": {
        "id": "user-uuid",
        "name": "John Doe"
      },
      "timestamp": "2026-01-11T20:00:00Z",
      "data": {
        "description": "Dinner at Italian restaurant",
        "amount": 120.00
      }
    },
    {
      "action": "updated",
      "actor": {
        "id": "user-uuid",
        "name": "John Doe"
      },
      "timestamp": "2026-01-11T22:00:00Z",
      "changes": {
        "description": {
          "from": "Dinner at Italian restaurant",
          "to": "Dinner at French restaurant"
        },
        "amount": {
          "from": 120.00,
          "to": 130.00
        }
      }
    }
  ]
}
```

---

## Bulk Operations

### Bulk Delete

**Request**
```json
DELETE /api/v1/groups/{group_id}/expenses/bulk
Authorization: Bearer <access_token>
{
  "expense_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

**Response**
```json
HTTP 200 OK
{
  "deleted": 3,
  "failed": 0,
  "message": "3 expenses deleted"
}
```

### Bulk Category Update

**Request**
```json
PATCH /api/v1/groups/{group_id}/expenses/bulk
Authorization: Bearer <access_token>
{
  "expense_ids": ["uuid-1", "uuid-2"],
  "updates": {
    "category": "Transport"
  }
}
```

**Response**
```json
HTTP 200 OK
{
  "updated": 2,
  "message": "2 expenses updated"
}
```

---

## Acceptance Criteria

### View List
- [ ] All expenses are displayed
- [ ] Pagination works correctly
- [ ] Sorting options work
- [ ] My share is calculated correctly

### View Details
- [ ] All expense information is displayed
- [ ] Splits show all participants
- [ ] Receipt is viewable
- [ ] Comments and reactions shown

### Filtering
- [ ] Single filter works
- [ ] Multiple filters work together
- [ ] Search finds matching expenses
- [ ] Presets apply correct filters

### Edit
- [ ] Creator can edit own expense
- [ ] Admin can edit any expense
- [ ] Member cannot edit others' expenses
- [ ] Balances update after edit
- [ ] Participants notified

### Delete
- [ ] Creator can delete own expense
- [ ] Admin can delete any expense
- [ ] Member cannot delete others' expenses
- [ ] Balances update after delete
- [ ] Soft delete allows recovery

### Receipt
- [ ] Can upload receipt with expense
- [ ] Can add receipt later
- [ ] Can replace receipt
- [ ] Can delete receipt
- [ ] Invalid files rejected
