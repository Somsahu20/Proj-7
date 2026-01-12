# Record Payment

## Overview

When a user pays someone outside the app (cash, bank transfer, etc.), they record the payment in the app to update balances and create a record.

---

## Record Payment Flow

### User Story
> As a user who owes money, I want to record my payment so that my debt is cleared once confirmed.

### Flow
1. User pays receiver offline
2. User opens app and records payment
3. Receiver gets notification
4. Receiver confirms or rejects
5. If confirmed, balances updated

---

## Basic Payment Recording

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/payments
Authorization: Bearer <access_token>
{
  "receiver_id": "user-uuid",
  "amount": 50.00,
  "description": "Settlement payment",
  "payment_method": "bank_transfer",
  "date": "2026-01-11"
}
```

### Payment Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| receiver_id | uuid | Yes | Who received the payment |
| amount | decimal | Yes | Payment amount |
| description | string | No | Optional note |
| payment_method | enum | No | How payment was made |
| date | date | No | When payment was made (default: today) |
| proof | file | No | Receipt/screenshot |

### Payment Methods

| Value | Description |
|-------|-------------|
| `cash` | Cash payment |
| `bank_transfer` | Bank transfer |
| `upi` | UPI payment |
| `other` | Other method |

**Response**
```json
HTTP 201 Created
{
  "id": "payment-uuid",
  "payer": {
    "id": "user-uuid-1",
    "name": "John Doe"
  },
  "receiver": {
    "id": "user-uuid-2",
    "name": "Jane Smith"
  },
  "amount": 50.00,
  "description": "Settlement payment",
  "payment_method": "bank_transfer",
  "status": "pending",
  "date": "2026-01-11",
  "created_at": "2026-01-11T15:00:00Z"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Invalid receiver | `{"detail": "Receiver must be a group member"}` |
| 400 | Invalid amount | `{"detail": "Amount must be greater than 0"}` |
| 400 | Self payment | `{"detail": "Cannot record payment to yourself"}` |
| 400 | Future date | `{"detail": "Payment date cannot be in the future"}` |

---

## Payment with Proof

### User Story
> As a payer, I want to attach proof of payment so the receiver can verify.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/payments
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

payment_data: {
  "receiver_id": "user-uuid",
  "amount": 50.00,
  "description": "Bank transfer",
  "payment_method": "bank_transfer"
}
proof: <file>
```

**Validation**
| Rule | Value |
|------|-------|
| Max file size | 5 MB |
| Allowed types | image/jpeg, image/png, image/webp, application/pdf |

**Response**
```json
HTTP 201 Created
{
  "id": "payment-uuid",
  "...": "...",
  "proof_url": "/uploads/payments/uuid/proof.jpg",
  "status": "pending"
}
```

---

## Suggested Payment Amount

### User Story
> As a user, I want to see the suggested payment amount based on my balance.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/payments/suggested
Authorization: Bearer <access_token>
Query Parameters:
  - receiver_id: uuid (optional)
```

**Response**
```json
HTTP 200 OK
{
  "suggestions": [
    {
      "receiver_id": "user-uuid-2",
      "receiver_name": "Jane Smith",
      "amount": 50.00,
      "reason": "You owe Jane $50.00"
    },
    {
      "receiver_id": "user-uuid-3",
      "receiver_name": "Bob Wilson",
      "amount": 25.00,
      "reason": "You owe Bob $25.00"
    }
  ]
}
```

---

## Partial Payment

### User Story
> As a user, I want to make a partial payment if I can't pay the full amount.

### Technical Requirements
Partial payments are fully supported. The user simply records the amount they actually paid.

**Example**
- User owes $100
- User pays $40
- Records $40 payment
- Remaining balance: $60

```json
POST /api/v1/groups/{group_id}/payments
{
  "receiver_id": "user-uuid",
  "amount": 40.00,
  "description": "Partial payment - will pay rest next week"
}
```

### Balance Updates
- Payment is recorded as pending
- When confirmed, balance reduced by payment amount
- Remaining balance still owed

---

## Payment Context

### From Specific Expense

**Request**
```json
POST /api/v1/groups/{group_id}/payments
{
  "receiver_id": "user-uuid",
  "amount": 30.00,
  "expense_id": "expense-uuid",
  "description": "Payment for dinner expense"
}
```

Linking to expense provides context but doesn't affect balance calculation (balances are aggregated).

### General Settlement

**Request**
```json
POST /api/v1/groups/{group_id}/payments
{
  "receiver_id": "user-uuid",
  "amount": 75.00,
  "description": "Settling up for the month"
}
```

---

## Cancel Pending Payment

### User Story
> As a payer, I want to cancel a payment I recorded by mistake.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/payments/{payment_id}/cancel
Authorization: Bearer <access_token>
{
  "reason": "Recorded wrong amount"
}
```

**Response**
```json
HTTP 200 OK
{
  "id": "payment-uuid",
  "status": "cancelled",
  "cancelled_at": "2026-01-11T16:00:00Z",
  "cancelled_reason": "Recorded wrong amount"
}
```

**Constraints**
- Can only cancel pending payments
- Cannot cancel confirmed or rejected payments

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Not pending | `{"detail": "Can only cancel pending payments"}` |
| 403 | Not payer | `{"detail": "Only the payer can cancel this payment"}` |

---

## Quick Settle

### User Story
> As a user, I want to quickly record a payment for the exact amount I owe.

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/payments/settle
Authorization: Bearer <access_token>
{
  "receiver_id": "user-uuid"
}
```

This automatically uses the full amount owed to that person.

**Response**
```json
HTTP 201 Created
{
  "id": "payment-uuid",
  "amount": 75.00,
  "description": "Full settlement",
  "status": "pending"
}
```

---

## Side Effects

When a payment is recorded:
1. **Payment Created**: With `pending` status
2. **Notification Sent**: To receiver (email based on preferences)
3. **SSE Broadcast**: Real-time update to receiver
4. **Activity Logged**: In group activity

Note: Balances are NOT updated until payment is confirmed.

---

## Acceptance Criteria

### Basic Recording
- [ ] User can record payment to group member
- [ ] Amount and receiver are required
- [ ] Description is optional
- [ ] Payment method is optional

### Validation
- [ ] Cannot pay self
- [ ] Amount must be positive
- [ ] Receiver must be group member
- [ ] Future date rejected

### With Proof
- [ ] Can upload image/PDF
- [ ] Invalid files rejected
- [ ] Proof is viewable

### Suggested Amount
- [ ] Shows what user owes
- [ ] Accurate based on current balance
- [ ] Can be used to auto-fill form

### Partial Payment
- [ ] Can pay less than owed
- [ ] Remaining balance calculated correctly

### Cancel
- [ ] Payer can cancel pending payment
- [ ] Cannot cancel confirmed/rejected
- [ ] Reason is recorded

### Notifications
- [ ] Receiver gets email notification
- [ ] Real-time SSE update sent
- [ ] Activity logged in group
