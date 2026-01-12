# Debt Simplification

## Overview

Debt simplification reduces the number of transactions needed to settle all debts. Instead of everyone paying everyone, the algorithm finds the minimum set of payments.

---

## The Problem

### Without Simplification

```
A owes B: $30
B owes C: $20
C owes A: $10

Naive: 3 transactions
A → B: $30
B → C: $20
C → A: $10
```

### With Simplification

```
Net positions:
A: -$30 + $10 = -$20 (owes)
B: +$30 - $20 = +$10 (owed)
C: +$20 - $10 = +$10 (owed)

Optimized: 2 transactions
A → B: $10
A → C: $10
```

---

## Algorithm

### Minimum Cash Flow Algorithm

The algorithm minimizes the number of transactions by:

1. Calculate net balance for each person
2. Find the person who owes the most (max debtor)
3. Find the person who is owed the most (max creditor)
4. Transfer the minimum of what's owed
5. Repeat until all balanced

### Pseudocode

```python
def simplify_debts(balances: dict[str, Decimal]) -> list[Transaction]:
    transactions = []

    while True:
        # Find max creditor and max debtor
        creditors = {k: v for k, v in balances.items() if v > 0}
        debtors = {k: v for k, v in balances.items() if v < 0}

        if not creditors or not debtors:
            break

        max_creditor = max(creditors, key=creditors.get)
        max_debtor = min(debtors, key=debtors.get)

        # Amount to transfer
        amount = min(creditors[max_creditor], abs(debtors[max_debtor]))

        # Create transaction
        transactions.append({
            'from': max_debtor,
            'to': max_creditor,
            'amount': amount
        })

        # Update balances
        balances[max_creditor] -= amount
        balances[max_debtor] += amount

        # Clean up zero balances
        balances = {k: v for k, v in balances.items() if v != 0}

    return transactions
```

---

## API Endpoint

### Get Simplified Debts

**Request**
```
GET /api/v1/groups/{group_id}/balances/simplified
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "original_transactions": 5,
  "simplified_transactions": 3,
  "reduction": "40%",
  "settlements": [
    {
      "from": {"id": "uuid-4", "name": "Alice Brown"},
      "to": {"id": "uuid-1", "name": "John Doe"},
      "amount": 287.50
    },
    {
      "from": {"id": "uuid-4", "name": "Alice Brown"},
      "to": {"id": "uuid-2", "name": "Jane Smith"},
      "amount": 25.50
    },
    {
      "from": {"id": "uuid-3", "name": "Bob Wilson"},
      "to": {"id": "uuid-2", "name": "Jane Smith"},
      "amount": 62.00
    }
  ],
  "total_amount": 375.00
}
```

---

## Example Scenarios

### Scenario 1: Simple Chain

**Input**
```
Alice paid $100 for dinner (Alice, Bob, Carol each owe $33.33)
Bob paid $60 for taxi (Alice, Bob, Carol each owe $20)
```

**Balances**
```
Alice: paid $100, owes $53.33 → balance: +$46.67
Bob: paid $60, owes $53.33 → balance: +$6.67
Carol: paid $0, owes $53.34 → balance: -$53.34
```

**Simplified Settlements**
```
Carol → Alice: $46.67
Carol → Bob: $6.67
```

### Scenario 2: Complex Web

**Input**
```
4 people, 10 expenses, various payers and splits
```

**Before Simplification**
```
A owes B: $50
A owes C: $30
B owes C: $40
B owes D: $20
C owes A: $25
C owes D: $15
D owes A: $35
D owes B: $10

Total: 8 transactions
```

**After Simplification**
```
Net balances:
A: -50 - 30 + 25 + 35 = -$20
B: +50 - 40 - 20 + 10 = $0
C: +30 + 40 - 25 - 15 = +$30
D: +20 + 15 - 35 - 10 = -$10

Simplified:
A → C: $20
D → C: $10

Total: 2 transactions (75% reduction)
```

---

## Preferences

### User Preferences

Some users may prefer specific settlement paths:

```json
GET /api/v1/groups/{group_id}/balances/simplified?preferences=true
```

**Response includes user preferences**
```json
{
  "settlements": [
    {
      "from": "Alice",
      "to": "John",
      "amount": 50.00,
      "preference_note": "Alice prefers bank transfer to John"
    }
  ]
}
```

### Maintaining Relationships

Option to keep certain pairs together even if not optimal:

```json
POST /api/v1/groups/{group_id}/balances/simplified
{
  "keep_pairs": [
    {"from": "uuid-1", "to": "uuid-2"}
  ]
}
```

---

## Edge Cases

### Single Debtor
```
Alice owes Bob, Carol, Dave

Simplified: Alice makes 3 separate payments
(No simplification possible)
```

### All Equal
```
Everyone owes the same per-person

Simplified: Maintain direct payments
```

### Near-Zero Balances
```
Balance: $0.02

Options:
- Include in settlement
- Forgive (admin action)
- Round to nearest dollar
```

---

## Complexity

### Time Complexity
O(n²) where n is the number of group members

### Space Complexity
O(n) for balance tracking

### Performance
- Up to 10 members: instant
- Up to 50 members: < 100ms
- Up to 100 members: < 500ms

---

## Acceptance Criteria

### Algorithm
- [ ] Correctly calculates net balances
- [ ] Minimizes number of transactions
- [ ] Total amounts are preserved
- [ ] All balances reach zero

### API
- [ ] Returns simplified settlement list
- [ ] Shows reduction percentage
- [ ] Handles edge cases gracefully

### Edge Cases
- [ ] Works with 2 members
- [ ] Works with 20+ members
- [ ] Handles exact zero balances
- [ ] Handles tiny remainders
