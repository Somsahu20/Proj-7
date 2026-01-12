# Expense Endpoints

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /groups/:id/expenses | List expenses |
| POST | /groups/:id/expenses | Create expense |
| GET | /groups/:id/expenses/:expenseId | Get expense |
| PATCH | /groups/:id/expenses/:expenseId | Update expense |
| DELETE | /groups/:id/expenses/:expenseId | Delete expense |
| POST | /groups/:id/expenses/:expenseId/receipt | Upload receipt |
| DELETE | /groups/:id/expenses/:expenseId/receipt | Remove receipt |
| GET | /groups/:id/expenses/:expenseId/history | Get history |
| GET | /groups/:id/categories | Get categories |
| POST | /groups/:id/categories | Create category |

---

## GET /groups/:id/expenses

### Query Parameters
- page, limit, sort
- category, payer_id, participant_id
- date_from, date_to
- amount_min, amount_max
- search

### Response 200
```json
{
  "expenses": [
    {
      "id": "uuid",
      "description": "Dinner",
      "amount": 120.00,
      "date": "2026-01-11",
      "payer": {...},
      "split_type": "equal",
      "participant_count": 4,
      "category": "Food & Drinks",
      "has_receipt": true,
      "my_share": 30.00
    }
  ],
  "pagination": {...}
}
```

---

## POST /groups/:id/expenses

### Request (Equal Split)
```json
{
  "description": "Dinner at restaurant",
  "amount": 120.00,
  "date": "2026-01-11",
  "payer_id": "uuid",
  "split_type": "equal",
  "participant_ids": ["uuid1", "uuid2", "uuid3", "uuid4"],
  "category": "Food & Drinks"
}
```

### Request (Unequal Split)
```json
{
  "description": "Dinner",
  "amount": 100.00,
  "split_type": "unequal",
  "splits": [
    {"user_id": "uuid1", "amount": 50.00},
    {"user_id": "uuid2", "amount": 30.00},
    {"user_id": "uuid3", "amount": 20.00}
  ]
}
```

### Response 201
Full expense object with splits.

---

## PATCH /groups/:id/expenses/:expenseId

### Request
```json
{
  "description": "Updated description",
  "amount": 130.00
}
```

### Response 200
Updated expense object.

---

## POST /groups/:id/expenses/:expenseId/receipt

### Request
```
Content-Type: multipart/form-data
file: <image/pdf>
```

### Response 200
```json
{
  "receipt_url": "/uploads/expenses/uuid/receipt.jpg"
}
```

---

## GET /groups/:id/expenses/:expenseId/history

### Response 200
```json
{
  "history": [
    {
      "version": 1,
      "action": "created",
      "actor": {...},
      "timestamp": "2026-01-11T18:00:00Z",
      "data": {...}
    },
    {
      "version": 2,
      "action": "updated",
      "changes": {
        "amount": {"from": 100, "to": 120}
      }
    }
  ]
}
```
