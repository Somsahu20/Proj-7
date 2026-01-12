# Settlement Flow

## Overview

The settlement flow guides users through paying off their debts efficiently, with bulk settlement options and optimization suggestions.

---

## Settlement Suggestions

### User Story
> As a user with debts, I want to see the best way to settle up.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/settlements/suggestions
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "my_balance": -125.50,
  "status": "you_owe",
  "suggestions": [
    {
      "pay_to": {
        "id": "uuid-1",
        "name": "John Doe",
        "profile_picture": "/uploads/profiles/uuid/photo.jpg"
      },
      "amount": 87.50,
      "reason": "Optimal settlement",
      "priority": "high"
    },
    {
      "pay_to": {
        "id": "uuid-2",
        "name": "Jane Smith"
      },
      "amount": 38.00,
      "reason": "Remaining balance",
      "priority": "medium"
    }
  ],
  "total_to_pay": 125.50,
  "simplified": true,
  "message": "Pay John $87.50 and Jane $38.00 to settle all debts"
}
```

---

## Bulk Settlement

### User Story
> As a user, I want to record multiple payments at once to settle all my debts.

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/settlements/bulk
Authorization: Bearer <access_token>
{
  "payments": [
    {
      "receiver_id": "uuid-1",
      "amount": 87.50,
      "payment_method": "bank_transfer"
    },
    {
      "receiver_id": "uuid-2",
      "amount": 38.00,
      "payment_method": "cash"
    }
  ],
  "note": "Settling up for the trip"
}
```

**Response**
```json
HTTP 201 Created
{
  "settlement_id": "settlement-uuid",
  "payments_created": 2,
  "total_amount": 125.50,
  "payments": [
    {
      "id": "payment-uuid-1",
      "receiver": "John Doe",
      "amount": 87.50,
      "status": "pending"
    },
    {
      "id": "payment-uuid-2",
      "receiver": "Jane Smith",
      "amount": 38.00,
      "status": "pending"
    }
  ],
  "message": "2 payments recorded. Awaiting confirmation from recipients."
}
```

---

## Quick Settle All

### User Story
> As a user, I want to quickly settle all my debts with one action.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/settlements/settle-all
Authorization: Bearer <access_token>
{
  "payment_method": "bank_transfer"
}
```

This creates payments for the optimized settlement amounts.

**Response**
```json
HTTP 201 Created
{
  "payments_created": 2,
  "total_amount": 125.50,
  "message": "All debts recorded for settlement"
}
```

---

## Settlement Status

### User Story
> As a user, I want to track the status of my settlements.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/settlements/status
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "group_id": "uuid",
  "is_settled": false,
  "my_status": {
    "balance": -75.50,
    "pending_payments": 2,
    "pending_amount": 125.50,
    "awaiting_confirmation": 50.00
  },
  "group_status": {
    "total_outstanding": 375.00,
    "members_with_debt": 2,
    "members_owed": 2,
    "pending_payments": 4
  },
  "recent_activity": [
    {
      "type": "payment_confirmed",
      "from": "Bob",
      "to": "John",
      "amount": 50.00,
      "timestamp": "2026-01-11T10:00:00Z"
    }
  ]
}
```

---

## Mark as Settled

### Forgive Small Amounts

**Request**
```json
POST /api/v1/groups/{group_id}/settlements/forgive
Authorization: Bearer <access_token>
{
  "debtor_id": "uuid",
  "amount": 0.50,
  "reason": "Rounding difference"
}
```

Only admin can forgive debts over $1.

**Response**
```json
HTTP 200 OK
{
  "message": "Forgave $0.50 owed by Alice",
  "new_balance": 0.00
}
```

### Mark Group as Settled

When all balances are zero:

**Request**
```
POST /api/v1/groups/{group_id}/settlements/complete
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Group is fully settled!",
  "settled_at": "2026-01-11T15:00:00Z",
  "statistics": {
    "total_expenses": 1250.50,
    "total_payments": 12,
    "duration_days": 14
  }
}
```

---

## Settlement Reminders

### User Story
> As a user who is owed money, I want to send reminders to debtors.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/settlements/remind
Authorization: Bearer <access_token>
{
  "debtor_id": "uuid",
  "message": "Hey, just a friendly reminder about the trip expenses!"
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "Reminder sent to Alice",
  "amount_owed": 125.50
}
```

### Bulk Remind

**Request**
```
POST /api/v1/groups/{group_id}/settlements/remind-all
Authorization: Bearer <access_token>
```

Sends reminders to all group members who owe money.

---

## Settlement Timeline

### User Story
> As a group admin, I want to see the settlement progress over time.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/settlements/timeline
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "timeline": [
    {
      "date": "2026-01-01",
      "total_debt": 1250.50,
      "event": "Trip started"
    },
    {
      "date": "2026-01-05",
      "total_debt": 1000.00,
      "event": "Bob paid John $250.50"
    },
    {
      "date": "2026-01-10",
      "total_debt": 750.00,
      "event": "Carol paid Jane $250.00"
    },
    {
      "date": "2026-01-11",
      "total_debt": 375.00,
      "event": "Multiple payments"
    }
  ],
  "projected_settlement": "2026-01-15",
  "progress_percentage": 70
}
```

---

## Partial Settlement

### User Story
> As a user, I want to pay part of what I owe if I can't pay everything now.

Partial payments are fully supported. The user simply records the amount they're paying:

```json
POST /api/v1/groups/{group_id}/payments
{
  "receiver_id": "uuid",
  "amount": 50.00,
  "description": "Partial payment - will pay rest next week"
}
```

The remaining balance is tracked and can be settled later.

---

## Settlement Notifications

### Celebration on Full Settlement

When a user's balance reaches zero:

```
🎉 Congratulations! You're all settled up in "Trip to Paris"!

Summary:
- Total expenses: $1,250.50
- Your share: $312.50
- You paid: $600.00
- Received: $287.50
- Duration: 14 days

Great job keeping finances clear!
```

### Group Fully Settled

When all group members reach zero balance:

```
🎊 "Trip to Paris" is fully settled!

The group is completely balanced. All debts have been paid.

Trip Statistics:
- 4 members
- 25 expenses
- $1,250.50 total
- 14 days duration

Would you like to archive this group?
[Archive Group] [Keep Active]
```

---

## Acceptance Criteria

### Suggestions
- [ ] Shows who to pay
- [ ] Amounts are optimized
- [ ] Considers debt simplification

### Bulk Settlement
- [ ] Can record multiple payments
- [ ] All payments created correctly
- [ ] Proper error handling

### Quick Settle
- [ ] One-click settlement
- [ ] Uses optimal amounts
- [ ] Creates pending payments

### Reminders
- [ ] Can remind individual
- [ ] Can remind all debtors
- [ ] Rate limiting applies

### Status Tracking
- [ ] Shows settlement progress
- [ ] Timeline is accurate
- [ ] Projection is reasonable

### Forgiveness
- [ ] Admin can forgive small amounts
- [ ] Larger amounts need confirmation
- [ ] Balance updates correctly
