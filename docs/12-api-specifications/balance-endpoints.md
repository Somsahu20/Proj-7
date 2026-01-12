# Balance Endpoints

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /users/me/balances | My balances across groups |
| GET | /groups/:id/balances | Group balances |
| GET | /groups/:id/balances/pairwise | Pairwise balances |
| GET | /groups/:id/balances/simplified | Simplified settlements |
| GET | /groups/:id/balances/cycles | Detect circular debts |
| GET | /groups/:id/settlements/suggestions | Settlement suggestions |
| POST | /groups/:id/settlements/bulk | Bulk settle |

---

## GET /users/me/balances

### Response 200
```json
{
  "total_balance": -75.50,
  "total_owed_to_me": 150.00,
  "total_i_owe": 225.50,
  "by_group": [
    {
      "group_id": "uuid",
      "group_name": "Trip to Paris",
      "balance": -125.50
    }
  ]
}
```

---

## GET /groups/:id/balances

### Response 200
```json
{
  "group_id": "uuid",
  "is_settled": false,
  "total_expenses": 1250.50,
  "balances": [
    {
      "user_id": "uuid",
      "name": "John Doe",
      "balance": 287.50,
      "paid": 600.00,
      "owes": 312.50
    }
  ],
  "debts": [
    {
      "from": {"id": "uuid", "name": "Alice"},
      "to": {"id": "uuid", "name": "John"},
      "amount": 287.50
    }
  ]
}
```

---

## GET /groups/:id/balances/simplified

### Response 200
```json
{
  "original_transactions": 5,
  "simplified_transactions": 3,
  "reduction": "40%",
  "settlements": [
    {
      "from": {...},
      "to": {...},
      "amount": 287.50
    }
  ]
}
```

---

## GET /groups/:id/balances/cycles

### Response 200
```json
{
  "has_cycles": true,
  "cycles": [
    {
      "participants": ["Alice", "Bob", "Carol"],
      "min_reducible": 20.00
    }
  ]
}
```

---

## GET /groups/:id/settlements/suggestions

### Response 200
```json
{
  "my_balance": -125.50,
  "suggestions": [
    {
      "pay_to": {...},
      "amount": 87.50,
      "priority": "high"
    }
  ],
  "total_to_pay": 125.50
}
```

---

## POST /groups/:id/settlements/bulk

### Request
```json
{
  "payments": [
    {"receiver_id": "uuid", "amount": 87.50},
    {"receiver_id": "uuid", "amount": 38.00}
  ]
}
```

### Response 201
```json
{
  "payments_created": 2,
  "total_amount": 125.50
}
```
