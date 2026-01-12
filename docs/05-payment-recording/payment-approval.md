# Payment Approval

## Overview

When a payer records a payment, the receiver must confirm or reject it. This two-party confirmation ensures both parties agree the payment was made.

---

## Payment States

```
┌─────────┐
│ PENDING │───────────────┐
└────┬────┘               │
     │                    │
     ├─── Confirm ───▶ ┌──┴───────┐
     │                 │CONFIRMED │
     │                 └──────────┘
     │
     ├─── Reject ────▶ ┌──────────┐
     │                 │ REJECTED │
     │                 └──────────┘
     │
     └─── Cancel ────▶ ┌──────────┐
        (by payer)     │CANCELLED │
                       └──────────┘
```

---

## View Pending Payments

### User Story
> As a receiver, I want to see payments waiting for my confirmation.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/payments/pending
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "pending_payments": [
    {
      "id": "payment-uuid-1",
      "payer": {
        "id": "user-uuid",
        "name": "John Doe",
        "profile_picture": "/uploads/profiles/uuid/photo.jpg"
      },
      "amount": 50.00,
      "description": "Settlement for dinner",
      "payment_method": "bank_transfer",
      "proof_url": "/uploads/payments/uuid/proof.jpg",
      "group": {
        "id": "group-uuid",
        "name": "Trip to Paris"
      },
      "date": "2026-01-11",
      "created_at": "2026-01-11T15:00:00Z"
    }
  ],
  "total": 1
}
```

---

## Confirm Payment

### User Story
> As a receiver, I want to confirm a payment I received so the debt is settled.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/payments/{payment_id}/confirm
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "id": "payment-uuid",
  "status": "confirmed",
  "confirmed_at": "2026-01-11T16:00:00Z",
  "payer": {
    "id": "user-uuid",
    "name": "John Doe",
    "new_balance": -25.00
  },
  "receiver": {
    "id": "user-uuid",
    "name": "Jane Smith",
    "new_balance": 25.00
  },
  "message": "Payment confirmed. Balances have been updated."
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not receiver | `{"detail": "Only the receiver can confirm this payment"}` |
| 400 | Not pending | `{"detail": "Payment is not pending"}` |

### Side Effects
1. **Status Updated**: To `confirmed`
2. **Balances Updated**:
   - Payer's balance increased by amount
   - Receiver's balance decreased by amount
3. **Notification Sent**: To payer confirming receipt
4. **SSE Broadcast**: Real-time update
5. **Activity Logged**: In group

---

## Reject Payment

### User Story
> As a receiver, I want to reject a payment if I didn't receive it or the amount is wrong.

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/payments/{payment_id}/reject
Authorization: Bearer <access_token>
{
  "reason": "Did not receive this payment"
}
```

**Rejection Reasons** (Predefined + Custom)
| Value | Description |
|-------|-------------|
| `not_received` | Payment was not received |
| `wrong_amount` | Amount doesn't match what was received |
| `wrong_method` | Payment method is incorrect |
| `other` | Other reason (requires explanation) |

**Response**
```json
HTTP 200 OK
{
  "id": "payment-uuid",
  "status": "rejected",
  "rejected_at": "2026-01-11T16:00:00Z",
  "rejected_reason": "Did not receive this payment",
  "message": "Payment has been rejected. The payer has been notified."
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not receiver | `{"detail": "Only the receiver can reject this payment"}` |
| 400 | Not pending | `{"detail": "Payment is not pending"}` |

### Side Effects
1. **Status Updated**: To `rejected`
2. **Balances Unchanged**: No balance updates
3. **Notification Sent**: To payer with rejection reason
4. **SSE Broadcast**: Real-time update
5. **Activity Logged**: In group

---

## Dispute Rejected Payment

### User Story
> As a payer whose payment was rejected, I want to dispute if I believe the rejection is incorrect.

### Flow
1. Payment rejected by receiver
2. Payer disagrees with rejection
3. Payer opens dispute
4. Both parties can add comments/evidence
5. Group admin can mediate
6. Resolution: confirm payment or maintain rejection

### Technical Requirements

**Open Dispute**
```json
POST /api/v1/groups/{group_id}/payments/{payment_id}/dispute
Authorization: Bearer <access_token>
{
  "reason": "I have bank confirmation that payment was sent",
  "evidence_urls": ["/uploads/payments/uuid/bank_receipt.jpg"]
}
```

**Response**
```json
HTTP 200 OK
{
  "id": "payment-uuid",
  "status": "disputed",
  "dispute": {
    "opened_at": "2026-01-11T17:00:00Z",
    "opened_by": "John Doe",
    "reason": "I have bank confirmation that payment was sent"
  }
}
```

**Resolve Dispute (Admin)**
```json
POST /api/v1/groups/{group_id}/payments/{payment_id}/dispute/resolve
Authorization: Bearer <access_token>
{
  "resolution": "confirm",
  "notes": "Bank receipt verified payment was made"
}
```

| Resolution | Effect |
|------------|--------|
| `confirm` | Payment marked confirmed, balances updated |
| `reject` | Payment remains rejected, no balance changes |

---

## Bulk Confirmation

### User Story
> As a receiver with multiple pending payments, I want to confirm them all at once.

### Technical Requirements

**Request**
```json
POST /api/v1/payments/confirm/bulk
Authorization: Bearer <access_token>
{
  "payment_ids": ["payment-uuid-1", "payment-uuid-2"]
}
```

**Response**
```json
HTTP 200 OK
{
  "confirmed": 2,
  "failed": 0,
  "results": [
    {"id": "payment-uuid-1", "status": "confirmed"},
    {"id": "payment-uuid-2", "status": "confirmed"}
  ]
}
```

---

## Reminder to Confirm

### User Story
> As a payer, I want to send a reminder if the receiver hasn't confirmed my payment.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/payments/{payment_id}/remind
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Reminder sent to Jane Smith"
}
```

**Constraints**
- Can only remind once per 24 hours
- Maximum 3 reminders per payment

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 429 | Too many reminders | `{"detail": "Please wait before sending another reminder"}` |

---

## Auto-Expiry (Optional)

### Configuration
Payments can auto-confirm if receiver doesn't respond within a timeframe.

| Setting | Description |
|---------|-------------|
| Disabled | No auto-confirm (default) |
| 7 days | Auto-confirm after 7 days |
| 14 days | Auto-confirm after 14 days |
| 30 days | Auto-confirm after 30 days |

This is a group-level setting controlled by admin.

---

## Notification Templates

### Payment Pending (to Receiver)
```
Subject: [GroupName] John Doe recorded a $50.00 payment to you

John Doe has recorded a payment of $50.00 to you in "Trip to Paris".

Payment details:
- Amount: $50.00
- Method: Bank Transfer
- Date: January 11, 2026
- Note: Settlement for dinner

Please confirm if you received this payment:
[Confirm Payment] [View Details]

If you did not receive this payment, you can reject it in the app.
```

### Payment Confirmed (to Payer)
```
Subject: [GroupName] Jane Smith confirmed your $50.00 payment

Good news! Jane Smith has confirmed receiving your payment of $50.00.

Your balance in "Trip to Paris" has been updated.
New balance: -$25.00

[View Group]
```

### Payment Rejected (to Payer)
```
Subject: [GroupName] Jane Smith rejected your $50.00 payment

Jane Smith has rejected your payment of $50.00 in "Trip to Paris".

Reason: Did not receive this payment

If you believe this is a mistake, please contact Jane or open a dispute.

[View Payment] [Contact Jane]
```

---

## Acceptance Criteria

### View Pending
- [ ] Receiver sees all pending payments
- [ ] Payment details are complete
- [ ] Proof is viewable if attached

### Confirm
- [ ] Only receiver can confirm
- [ ] Balances updated correctly
- [ ] Payer notified
- [ ] Activity logged

### Reject
- [ ] Only receiver can reject
- [ ] Reason is required
- [ ] Balances not updated
- [ ] Payer notified with reason

### Dispute
- [ ] Payer can dispute rejected payment
- [ ] Evidence can be attached
- [ ] Admin can resolve
- [ ] Both parties notified of resolution

### Reminders
- [ ] Payer can send reminder
- [ ] Rate limited appropriately
- [ ] Receiver gets notification

### Bulk Actions
- [ ] Can confirm multiple payments
- [ ] Failed confirmations reported
- [ ] All updates are atomic
