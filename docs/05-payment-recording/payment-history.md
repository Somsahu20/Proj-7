# Payment History

## Overview

Users can view a complete history of all payments they've made or received, with filtering and status tracking.

---

## View My Payment History

### User Story
> As a user, I want to see all payments I've made and received across all groups.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/payments
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20, max: 50)
  - type: string (sent | received | all)
  - status: string (pending | confirmed | rejected | cancelled | all)
  - start_date: date
  - end_date: date
```

**Response**
```json
HTTP 200 OK
{
  "payments": [
    {
      "id": "payment-uuid-1",
      "type": "sent",
      "amount": 50.00,
      "other_party": {
        "id": "user-uuid",
        "name": "Jane Smith",
        "profile_picture": "/uploads/profiles/uuid/photo.jpg"
      },
      "group": {
        "id": "group-uuid",
        "name": "Trip to Paris"
      },
      "description": "Settlement payment",
      "payment_method": "bank_transfer",
      "status": "confirmed",
      "has_proof": true,
      "date": "2026-01-11",
      "created_at": "2026-01-11T15:00:00Z",
      "confirmed_at": "2026-01-11T16:00:00Z"
    },
    {
      "id": "payment-uuid-2",
      "type": "received",
      "amount": 30.00,
      "other_party": {
        "id": "user-uuid",
        "name": "Bob Wilson"
      },
      "group": {
        "id": "group-uuid",
        "name": "Apartment 4B"
      },
      "description": "Rent share",
      "payment_method": "upi",
      "status": "pending",
      "has_proof": false,
      "date": "2026-01-10",
      "created_at": "2026-01-10T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15,
    "pages": 1
  },
  "summary": {
    "total_sent_confirmed": 250.00,
    "total_received_confirmed": 180.00,
    "pending_sent": 50.00,
    "pending_received": 30.00
  }
}
```

---

## View Group Payment History

### User Story
> As a group member, I want to see all payments within a specific group.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/payments
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20, max: 50)
  - status: string (pending | confirmed | rejected | all)
  - payer_id: uuid (optional filter)
  - receiver_id: uuid (optional filter)
  - start_date: date
  - end_date: date
```

**Response**
```json
HTTP 200 OK
{
  "payments": [
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
      "description": "Settlement",
      "payment_method": "cash",
      "status": "confirmed",
      "has_proof": false,
      "date": "2026-01-11",
      "created_at": "2026-01-11T15:00:00Z",
      "confirmed_at": "2026-01-11T16:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 8,
    "pages": 1
  },
  "summary": {
    "total_confirmed": 500.00,
    "total_pending": 75.00,
    "payment_count": 8
  }
}
```

---

## View Payment Details

### User Story
> As a group member, I want to see full details of a specific payment.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/payments/{payment_id}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "id": "payment-uuid",
  "payer": {
    "id": "user-uuid-1",
    "name": "John Doe",
    "profile_picture": "/uploads/profiles/uuid/photo.jpg"
  },
  "receiver": {
    "id": "user-uuid-2",
    "name": "Jane Smith",
    "profile_picture": "/uploads/profiles/uuid/photo.jpg"
  },
  "amount": 50.00,
  "description": "Settlement for dinner expenses",
  "payment_method": "bank_transfer",
  "status": "confirmed",
  "date": "2026-01-11",
  "proof_files": [
    {
      "id": "file-uuid",
      "url": "/uploads/payments/uuid/proof.jpg",
      "type": "image/jpeg"
    }
  ],
  "linked_expense": {
    "id": "expense-uuid",
    "description": "Dinner at restaurant"
  },
  "created_at": "2026-01-11T15:00:00Z",
  "confirmed_at": "2026-01-11T16:00:00Z",
  "history": [
    {
      "action": "created",
      "actor": "John Doe",
      "timestamp": "2026-01-11T15:00:00Z"
    },
    {
      "action": "confirmed",
      "actor": "Jane Smith",
      "timestamp": "2026-01-11T16:00:00Z"
    }
  ]
}
```

---

## Payment Status Timeline

### Status Transitions

```
┌─────────┐ create  ┌─────────┐
│         │────────▶│ PENDING │
└─────────┘         └────┬────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
┌─────────┐       ┌───────────┐       ┌───────────┐
│CONFIRMED│       │ REJECTED  │       │ CANCELLED │
└─────────┘       └───────────┘       └───────────┘
                         │
                         ▼
                  ┌───────────┐
                  │ DISPUTED  │
                  └─────┬─────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       ┌───────────┐       ┌───────────┐
       │ CONFIRMED │       │ REJECTED  │
       └───────────┘       └───────────┘
```

### Status Details

| Status | Description | Can Transition To |
|--------|-------------|-------------------|
| `pending` | Awaiting receiver confirmation | confirmed, rejected, cancelled |
| `confirmed` | Receiver confirmed receipt | (terminal) |
| `rejected` | Receiver rejected payment | disputed |
| `cancelled` | Payer cancelled | (terminal) |
| `disputed` | Payer disputes rejection | confirmed, rejected |

---

## Payment Statistics

### User Story
> As a user, I want to see my payment statistics.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/payments/statistics
Authorization: Bearer <access_token>
Query Parameters:
  - period: string (this_month | last_month | this_year | all_time)
```

**Response**
```json
HTTP 200 OK
{
  "period": {
    "start": "2026-01-01",
    "end": "2026-01-31"
  },
  "sent": {
    "total": 350.00,
    "count": 5,
    "confirmed": 300.00,
    "pending": 50.00
  },
  "received": {
    "total": 200.00,
    "count": 3,
    "confirmed": 180.00,
    "pending": 20.00
  },
  "by_method": [
    {"method": "bank_transfer", "count": 4, "amount": 300.00},
    {"method": "cash", "count": 3, "amount": 200.00},
    {"method": "upi", "count": 1, "amount": 50.00}
  ],
  "by_group": [
    {"group_id": "uuid-1", "group_name": "Trip to Paris", "net": -150.00},
    {"group_id": "uuid-2", "group_name": "Apartment", "net": 100.00}
  ]
}
```

---

## Export Payment History

### User Story
> As a user, I want to export my payment history for record-keeping.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/payments/export
Authorization: Bearer <access_token>
Query Parameters:
  - format: string (csv | pdf)
  - start_date: date
  - end_date: date
```

**Response (CSV)**
```
HTTP 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="payments_2026-01.csv"

Date,Type,Amount,Other Party,Group,Status,Method,Description
2026-01-11,Sent,50.00,Jane Smith,Trip to Paris,Confirmed,Bank Transfer,Settlement
2026-01-10,Received,30.00,Bob Wilson,Apartment,Pending,UPI,Rent share
```

**Response (PDF)**
Returns a formatted PDF document with payment history.

---

## Search Payments

### User Story
> As a user, I want to search for specific payments.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/payments/search
Authorization: Bearer <access_token>
Query Parameters:
  - q: string (search term)
  - limit: int (default: 10)
```

Searches in:
- Payment description
- Other party name
- Group name

**Response**
```json
HTTP 200 OK
{
  "results": [
    {
      "id": "payment-uuid",
      "type": "sent",
      "amount": 50.00,
      "other_party": "Jane Smith",
      "group": "Trip to Paris",
      "match": "description: Settlement for dinner"
    }
  ],
  "total": 1
}
```

---

## Filters and Sorting

### Available Filters

| Filter | Values |
|--------|--------|
| type | sent, received, all |
| status | pending, confirmed, rejected, cancelled, all |
| start_date | YYYY-MM-DD |
| end_date | YYYY-MM-DD |
| min_amount | number |
| max_amount | number |
| payment_method | cash, bank_transfer, upi, other |
| group_id | UUID |

### Sorting Options

| Sort | Description |
|------|-------------|
| date_desc | Newest first (default) |
| date_asc | Oldest first |
| amount_desc | Highest amount first |
| amount_asc | Lowest amount first |

---

## Acceptance Criteria

### View History
- [ ] User can see sent payments
- [ ] User can see received payments
- [ ] All payment details displayed
- [ ] Pagination works correctly

### Filters
- [ ] Filter by type works
- [ ] Filter by status works
- [ ] Date range filter works
- [ ] Multiple filters combine correctly

### Statistics
- [ ] Totals are accurate
- [ ] Period filtering works
- [ ] Breakdown by method is correct
- [ ] Breakdown by group is correct

### Export
- [ ] CSV export works
- [ ] PDF export works
- [ ] Date range is respected
- [ ] All relevant data included

### Search
- [ ] Searches descriptions
- [ ] Searches party names
- [ ] Searches group names
- [ ] Results are relevant
