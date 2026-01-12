# Expense Creation

## Overview

Users can add expenses to track shared costs within a group. Each expense records who paid, who participated, and how the cost should be split.

---

## Add Expense

### User Story
> As a group member, I want to add an expense so that the cost can be tracked and split among participants.

### Expense Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| description | string | Yes | What the expense was for |
| amount | decimal | Yes | Total amount paid |
| date | date | Yes | When the expense occurred |
| payer_id | uuid | Yes | Who paid for this expense |
| participants | array | Yes | Who shares this expense |
| split_type | enum | Yes | How to split the cost |
| category | string | No | Expense category |
| receipt | file | No | Receipt image/document |
| notes | string | No | Additional notes |

### Technical Requirements

**Basic Request (Equal Split)**
```json
POST /api/v1/groups/{group_id}/expenses
Authorization: Bearer <access_token>
{
  "description": "Dinner at Italian restaurant",
  "amount": 120.00,
  "date": "2026-01-11",
  "payer_id": "user-uuid-1",
  "split_type": "equal",
  "participant_ids": ["user-uuid-1", "user-uuid-2", "user-uuid-3", "user-uuid-4"],
  "category": "Food & Drinks"
}
```

**Validation Rules**
| Field | Rules |
|-------|-------|
| description | 1-200 chars, not empty |
| amount | > 0, max 2 decimal places, max 999999.99 |
| date | Not in future (can be past) |
| payer_id | Must be group member |
| participant_ids | At least 1, all must be group members |
| split_type | equal, unequal, shares, percentage |

**Response (Success)**
```json
HTTP 201 Created
{
  "id": "expense-uuid",
  "description": "Dinner at Italian restaurant",
  "amount": 120.00,
  "date": "2026-01-11",
  "payer": {
    "id": "user-uuid-1",
    "name": "John Doe"
  },
  "split_type": "equal",
  "splits": [
    {
      "user_id": "user-uuid-1",
      "name": "John Doe",
      "amount": 30.00,
      "is_payer": true
    },
    {
      "user_id": "user-uuid-2",
      "name": "Jane Smith",
      "amount": 30.00,
      "is_payer": false
    },
    {
      "user_id": "user-uuid-3",
      "name": "Bob Wilson",
      "amount": 30.00,
      "is_payer": false
    },
    {
      "user_id": "user-uuid-4",
      "name": "Alice Brown",
      "amount": 30.00,
      "is_payer": false
    }
  ],
  "category": "Food & Drinks",
  "created_by": {
    "id": "user-uuid-1",
    "name": "John Doe"
  },
  "created_at": "2026-01-11T20:00:00Z"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Invalid amount | `{"detail": "Amount must be greater than 0"}` |
| 400 | Payer not in group | `{"detail": "Payer must be a group member"}` |
| 400 | Invalid participant | `{"detail": "All participants must be group members"}` |
| 400 | Future date | `{"detail": "Expense date cannot be in the future"}` |
| 403 | Not group member | `{"detail": "You are not a member of this group"}` |

---

## Payer Selection

### Self as Payer (Default)
The current user is typically the payer, but any group member can be selected.

### Pay for Someone Else

**Use Case**: Recording an expense that someone else paid for.

```json
{
  "description": "Groceries",
  "amount": 50.00,
  "payer_id": "other-user-uuid",
  "...": "..."
}
```

Note: Only record expenses for others if they've asked you to or if you're an admin.

---

## Participant Selection

### All Group Members
Quick option to select everyone in the group.

### Subset of Members
Select specific members who participated.

### Exclude Self
Payer can be excluded from participants if they didn't benefit from the expense.

**Example**: John pays for a gift for Jane
```json
{
  "description": "Birthday gift for Jane",
  "amount": 60.00,
  "payer_id": "john-uuid",
  "participant_ids": ["bob-uuid", "alice-uuid"],
  "split_type": "equal"
}
```
Jane is excluded, John paid but doesn't owe himself.

---

## Multiple Payers

### User Story
> As a group member, I want to record an expense that was paid by multiple people.

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/expenses
{
  "description": "Hotel booking",
  "amount": 400.00,
  "date": "2026-01-10",
  "payers": [
    {"user_id": "user-uuid-1", "amount": 250.00},
    {"user_id": "user-uuid-2", "amount": 150.00}
  ],
  "split_type": "equal",
  "participant_ids": ["user-uuid-1", "user-uuid-2", "user-uuid-3", "user-uuid-4"]
}
```

**Validation**
- Sum of payer amounts must equal total expense amount
- All payers must be group members

**Balance Calculation**
For each participant:
- Owes: amount / participants = 100.00
- John paid 250, owes 100 → balance +150
- Jane paid 150, owes 100 → balance +50
- Bob paid 0, owes 100 → balance -100
- Alice paid 0, owes 100 → balance -100

---

## Receipt/Image Attachment

### User Story
> As a user, I want to attach a receipt to an expense for documentation.

### Upload with Expense Creation

**Request**
```
POST /api/v1/groups/{group_id}/expenses
Content-Type: multipart/form-data

expense_data: {...json...}
receipt: <file>
```

### Add Receipt Later

**Request**
```
POST /api/v1/groups/{group_id}/expenses/{expense_id}/receipt
Content-Type: multipart/form-data

file: <image/pdf>
```

**Response**
```json
HTTP 200 OK
{
  "receipt_url": "/uploads/expenses/uuid/receipt.jpg"
}
```

**Validation**
| Rule | Value |
|------|-------|
| Max file size | 5 MB |
| Allowed types | image/jpeg, image/png, image/webp, application/pdf |

---

## Expense Notes

### User Story
> As a user, I want to add notes to an expense to provide context.

**Request**
```json
{
  "description": "Uber to airport",
  "amount": 45.00,
  "notes": "Split 3 ways, Alice wasn't with us for this ride"
}
```

Notes are optional and can be up to 500 characters.

---

## Quick Expense (Simplified)

### User Story
> As a user, I want to quickly add a simple expense without too many options.

### Quick Add Flow
1. Enter amount
2. Enter description
3. Select "paid by me, split equally with everyone"
4. Submit

**Request**
```json
POST /api/v1/groups/{group_id}/expenses/quick
{
  "description": "Coffee",
  "amount": 15.00
}
```

**Defaults Applied**
- Payer: Current user
- Participants: All group members
- Split type: Equal
- Date: Today
- Category: None

---

## Duplicate Expense Detection

### Overview
Warn users if a similar expense was recently added to prevent accidental duplicates.

### Detection Criteria
- Same amount (within 1%)
- Same date (within 24 hours)
- Similar description (fuzzy match)

**Response with Warning**
```json
HTTP 201 Created
{
  "id": "expense-uuid",
  "...": "...",
  "warning": {
    "type": "possible_duplicate",
    "message": "A similar expense was added recently",
    "similar_expense": {
      "id": "other-expense-uuid",
      "description": "Coffee and snacks",
      "amount": 15.00,
      "date": "2026-01-11"
    }
  }
}
```

---

## Side Effects

When an expense is created:
1. **Balance Updated**: All affected members' balances recalculated
2. **Activity Logged**: Expense creation recorded in group activity
3. **Notifications Sent**: Participants notified (email based on preferences)
4. **SSE Broadcast**: Real-time update to connected group members

---

## Acceptance Criteria

### Basic Creation
- [ ] User can add expense with amount and description
- [ ] User can select payer
- [ ] User can select participants
- [ ] Expense appears in group expense list

### Validation
- [ ] Invalid amounts are rejected
- [ ] Non-members cannot be selected
- [ ] Future dates are rejected
- [ ] Empty description is rejected

### Split Calculation
- [ ] Equal split divides evenly
- [ ] Payer's balance is correctly credited
- [ ] Participants' balances are correctly debited

### Receipt
- [ ] User can attach image with expense
- [ ] User can add receipt later
- [ ] Invalid files are rejected

### Notifications
- [ ] Participants receive notifications
- [ ] Payer does not receive notification
- [ ] Real-time update via SSE

### Edge Cases
- [ ] Single participant (payer only)
- [ ] Payer not in participants
- [ ] Multiple payers
- [ ] Duplicate detection works
