# Payment Endpoints

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /groups/:id/payments | List group payments |
| POST | /groups/:id/payments | Record payment |
| GET | /groups/:id/payments/:paymentId | Get payment details |
| POST | /groups/:id/payments/:paymentId/confirm | Confirm payment |
| POST | /groups/:id/payments/:paymentId/reject | Reject payment |
| POST | /groups/:id/payments/:paymentId/cancel | Cancel payment |
| POST | /groups/:id/payments/:paymentId/proof | Upload proof |
| GET | /users/me/payments | My payment history |
| GET | /users/me/payments/pending | Pending confirmations |

---

## POST /groups/:id/payments

### Request
```json
{
  "receiver_id": "uuid",
  "amount": 50.00,
  "description": "Settlement payment",
  "payment_method": "bank_transfer",
  "date": "2026-01-11"
}
```

### Response 201
```json
{
  "id": "uuid",
  "payer": {...},
  "receiver": {...},
  "amount": 50.00,
  "status": "pending",
  "payment_method": "bank_transfer",
  "created_at": "2026-01-11T15:00:00Z"
}
```

---

## POST /groups/:id/payments/:paymentId/confirm

### Request
No body required.

### Response 200
```json
{
  "id": "uuid",
  "status": "confirmed",
  "confirmed_at": "2026-01-11T16:00:00Z"
}
```

---

## POST /groups/:id/payments/:paymentId/reject

### Request
```json
{
  "reason": "Did not receive this payment"
}
```

### Response 200
```json
{
  "id": "uuid",
  "status": "rejected",
  "rejected_reason": "Did not receive this payment"
}
```

---

## POST /groups/:id/payments/:paymentId/proof

### Request
```
Content-Type: multipart/form-data
file: <image/pdf>
```

### Response 200
```json
{
  "proof_url": "/uploads/payments/uuid/proof.jpg"
}
```

---

## GET /users/me/payments

### Query Parameters
- type: sent | received | all
- status: pending | confirmed | rejected | all
- start_date, end_date
- page, limit

### Response 200
```json
{
  "payments": [
    {
      "id": "uuid",
      "type": "sent",
      "amount": 50.00,
      "other_party": {...},
      "group": {...},
      "status": "confirmed"
    }
  ],
  "summary": {
    "total_sent_confirmed": 250.00,
    "total_received_confirmed": 180.00
  }
}
```

---

## GET /users/me/payments/pending

### Response 200
```json
{
  "pending_payments": [
    {
      "id": "uuid",
      "payer": {...},
      "amount": 50.00,
      "group": {...},
      "created_at": "2026-01-11T15:00:00Z"
    }
  ],
  "total": 1
}
```
