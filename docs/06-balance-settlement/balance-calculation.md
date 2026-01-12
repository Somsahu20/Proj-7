# Balance Calculation

## Overview

The system maintains real-time balances for each user in each group. Balances are updated whenever expenses are added/modified or payments are confirmed.

---

## Balance Concepts

### Individual Balance
A user's net position in a group:
- Sum of amounts they've paid for others
- Minus sum of amounts others have paid for them
- Minus confirmed payments made
- Plus confirmed payments received

### Pairwise Balance
What one specific user owes another:
- Based on expenses where A paid and B participated
- Reduced by payments from B to A

---

## View My Balance

### User Story
> As a user, I want to see my balance across all groups.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/balances
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "total_balance": -75.50,
  "total_owed_to_me": 150.00,
  "total_i_owe": 225.50,
  "by_group": [
    {
      "group_id": "uuid-1",
      "group_name": "Trip to Paris",
      "balance": -125.50,
      "owed_to_me": 50.00,
      "i_owe": 175.50
    },
    {
      "group_id": "uuid-2",
      "group_name": "Apartment",
      "balance": 50.00,
      "owed_to_me": 100.00,
      "i_owe": 50.00
    }
  ]
}
```

---

## View Group Balances

### User Story
> As a group member, I want to see all balances in the group.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/balances
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "group_id": "uuid",
  "group_name": "Trip to Paris",
  "is_settled": false,
  "total_expenses": 1250.50,
  "balances": [
    {
      "user_id": "uuid-1",
      "name": "John Doe",
      "balance": 287.50,
      "paid": 600.00,
      "owes": 312.50,
      "is_settled": false
    },
    {
      "user_id": "uuid-2",
      "name": "Jane Smith",
      "balance": 87.50,
      "paid": 400.00,
      "owes": 312.50,
      "is_settled": false
    },
    {
      "user_id": "uuid-3",
      "name": "Bob Wilson",
      "balance": -62.00,
      "paid": 250.50,
      "owes": 312.50,
      "is_settled": false
    },
    {
      "user_id": "uuid-4",
      "name": "Alice Brown",
      "balance": -313.00,
      "paid": 0.00,
      "owes": 313.00,
      "is_settled": false
    }
  ],
  "debts": [
    {
      "from": {"id": "uuid-4", "name": "Alice Brown"},
      "to": {"id": "uuid-1", "name": "John Doe"},
      "amount": 287.50
    },
    {
      "from": {"id": "uuid-3", "name": "Bob Wilson"},
      "to": {"id": "uuid-2", "name": "Jane Smith"},
      "amount": 62.00
    },
    {
      "from": {"id": "uuid-4", "name": "Alice Brown"},
      "to": {"id": "uuid-2", "name": "Jane Smith"},
      "amount": 25.50
    }
  ]
}
```

---

## Balance Calculation Formula

### For Each User

```
balance = total_paid - total_share

where:
  total_paid = sum of (expense.amount where user is payer)
  total_share = sum of (user's split amount for each expense they're in)
```

### After Payments

```
effective_balance = balance - payments_made + payments_received

where:
  payments_made = sum of confirmed payments where user is payer
  payments_received = sum of confirmed payments where user is receiver
```

---

## Pairwise Balance

### User Story
> As a user, I want to see exactly how much I owe to or am owed by each person.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/balances/pairwise
Authorization: Bearer <access_token>
Query Parameters:
  - user_id: uuid (optional, filter to specific user)
```

**Response**
```json
HTTP 200 OK
{
  "pairwise_balances": [
    {
      "user_a": {"id": "uuid-1", "name": "John Doe"},
      "user_b": {"id": "uuid-2", "name": "Jane Smith"},
      "balance": 50.00,
      "description": "John is owed $50.00 by Jane"
    },
    {
      "user_a": {"id": "uuid-1", "name": "John Doe"},
      "user_b": {"id": "uuid-4", "name": "Alice Brown"},
      "balance": 237.50,
      "description": "John is owed $237.50 by Alice"
    }
  ]
}
```

### Calculation

```
pairwise_balance(A, B) =
  sum(B's share in expenses paid by A)
  - sum(A's share in expenses paid by B)
  - sum(confirmed payments from B to A)
  + sum(confirmed payments from A to B)
```

---

## Balance History

### User Story
> As a user, I want to see how my balance changed over time.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/balances/history
Authorization: Bearer <access_token>
Query Parameters:
  - user_id: uuid (optional, default: current user)
  - start_date: date
  - end_date: date
```

**Response**
```json
HTTP 200 OK
{
  "user_id": "uuid-1",
  "history": [
    {
      "date": "2026-01-11",
      "balance": -125.50,
      "change": -30.00,
      "event": {
        "type": "expense_added",
        "description": "Dinner at restaurant",
        "amount": 30.00
      }
    },
    {
      "date": "2026-01-10",
      "balance": -95.50,
      "change": 50.00,
      "event": {
        "type": "payment_confirmed",
        "description": "Payment from Bob",
        "amount": 50.00
      }
    }
  ]
}
```

---

## Real-time Balance Updates

### SSE Events

When balance changes occur, an SSE event is broadcast:

```json
{
  "event": "balance:updated",
  "data": {
    "group_id": "uuid",
    "user_id": "uuid",
    "old_balance": -95.50,
    "new_balance": -125.50,
    "change": -30.00,
    "reason": "expense_added"
  }
}
```

### Update Triggers

| Event | Balance Effect |
|-------|----------------|
| Expense added | Payer balance up, participants balance down |
| Expense edited | Recalculate affected users |
| Expense deleted | Reverse the original calculation |
| Payment confirmed | Payer balance up, receiver balance down |

---

## Balance Precision

### Decimal Handling
- All amounts stored as DECIMAL(10,2)
- Calculations maintain cent precision
- Rounding uses HALF_UP

### Rounding Differences
Small rounding differences (< $0.05) may occur in complex splits. These are:
- Displayed as-is
- Tracked for transparency
- Can be forgiven by admin

---

## Acceptance Criteria

### My Balance
- [ ] Shows total across all groups
- [ ] Shows per-group breakdown
- [ ] Positive/negative clearly indicated
- [ ] Updates in real-time

### Group Balances
- [ ] All members listed with balances
- [ ] Shows who owes whom
- [ ] Totals are accurate
- [ ] Settled status is correct

### Pairwise
- [ ] Shows exact amounts between users
- [ ] Direction is clear (who owes whom)
- [ ] Matches overall balance

### History
- [ ] Tracks all balance changes
- [ ] Shows event that caused change
- [ ] Date filtering works

### Real-time
- [ ] SSE events sent on changes
- [ ] UI updates without refresh
- [ ] Multiple tabs stay in sync
