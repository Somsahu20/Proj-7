# Split Options

## Overview

The app supports four split methods to divide expenses among participants. Each method provides flexibility for different scenarios.

---

## Split Types

| Type | Description | Use Case |
|------|-------------|----------|
| `equal` | Divide evenly among all participants | Most common, everyone owes the same |
| `unequal` | Specify exact amounts per person | Different consumption or agreed amounts |
| `shares` | Proportional split based on shares | Room sharing, ticket quantities |
| `percentage` | Percentage-based split | Income-based or agreed percentages |

---

## Equal Split

### Description
The total amount is divided equally among all participants. Handles remainders by adding pennies to random participants.

### Request Format
```json
{
  "amount": 100.00,
  "split_type": "equal",
  "participant_ids": ["user-1", "user-2", "user-3"]
}
```

### Calculation
```
Total: $100.00
Participants: 3
Each owes: $100.00 / 3 = $33.33 (with $0.01 remainder)

Result:
- user-1: $33.34 (gets the extra penny)
- user-2: $33.33
- user-3: $33.33
```

### Remainder Handling
When amount doesn't divide evenly:
1. Calculate base amount per person
2. Calculate remainder in cents
3. Distribute extra cents randomly among participants
4. Ensure total always equals original amount

### Technical Details
```python
def equal_split(amount: Decimal, participants: list) -> list:
    count = len(participants)
    base_amount = (amount / count).quantize(Decimal('0.01'), ROUND_DOWN)
    remainder_cents = int((amount - (base_amount * count)) * 100)

    splits = [base_amount] * count
    for i in range(remainder_cents):
        splits[i] += Decimal('0.01')

    random.shuffle(splits)  # Randomize who gets extra cents
    return list(zip(participants, splits))
```

---

## Unequal Split

### Description
Specify exact amounts for each participant. User defines how much each person owes.

### Request Format
```json
{
  "amount": 100.00,
  "split_type": "unequal",
  "splits": [
    {"user_id": "user-1", "amount": 50.00},
    {"user_id": "user-2", "amount": 30.00},
    {"user_id": "user-3", "amount": 20.00}
  ]
}
```

### Validation
| Rule | Error Message |
|------|---------------|
| Sum must equal total | "Split amounts must equal expense total" |
| All amounts > 0 | "Split amounts must be positive" |
| All users must be members | "All participants must be group members" |

### Use Cases
- Someone had more expensive item at dinner
- One person only had drinks
- Different room rates at hotel

### Error Response
```json
HTTP 400 Bad Request
{
  "detail": "Split amounts ($95.00) do not equal expense total ($100.00)",
  "split_sum": 95.00,
  "expense_total": 100.00,
  "difference": 5.00
}
```

---

## Split by Shares

### Description
Assign shares to each participant and divide proportionally. Useful when quantities differ.

### Request Format
```json
{
  "amount": 200.00,
  "split_type": "shares",
  "splits": [
    {"user_id": "user-1", "shares": 2},
    {"user_id": "user-2", "shares": 1},
    {"user_id": "user-3", "shares": 1}
  ]
}
```

### Calculation
```
Total: $200.00
Total shares: 2 + 1 + 1 = 4
Per share: $200.00 / 4 = $50.00

Result:
- user-1: 2 shares × $50.00 = $100.00
- user-2: 1 share × $50.00 = $50.00
- user-3: 1 share × $50.00 = $50.00
```

### Validation
| Rule | Error Message |
|------|---------------|
| Shares must be positive integers | "Shares must be positive whole numbers" |
| At least 1 share per participant | "Each participant must have at least 1 share" |
| Total shares > 0 | "Total shares must be greater than 0" |

### Use Cases
- Hotel room (2 people in one room, 1 in another)
- Buying multiple tickets (different quantities)
- Shared cab (distance-based)

### UI Suggestions
- Quick options: 1, 2, 3, 4 shares
- Custom input for larger numbers
- Show calculated amount in real-time

---

## Split by Percentage

### Description
Assign percentages to each participant. Must total exactly 100%.

### Request Format
```json
{
  "amount": 150.00,
  "split_type": "percentage",
  "splits": [
    {"user_id": "user-1", "percentage": 50},
    {"user_id": "user-2", "percentage": 30},
    {"user_id": "user-3", "percentage": 20}
  ]
}
```

### Calculation
```
Total: $150.00

Result:
- user-1: 50% × $150.00 = $75.00
- user-2: 30% × $150.00 = $45.00
- user-3: 20% × $150.00 = $30.00
```

### Validation
| Rule | Error Message |
|------|---------------|
| Total must equal 100% | "Percentages must total 100%" |
| Each percentage > 0 | "Percentage must be positive" |
| Max 2 decimal places | "Percentage can have max 2 decimal places" |

### Remainder Handling
When percentages result in fractions of cents:
```
Total: $100.00
Split: 33.33%, 33.33%, 33.34%

Result:
- user-1: $33.33
- user-2: $33.33
- user-3: $33.34 (absorbs rounding)
```

### Use Cases
- Income-based rent split
- Agreed contribution ratios
- Couples with different financial situations

### Error Response
```json
HTTP 400 Bad Request
{
  "detail": "Percentages total 95%, must equal 100%",
  "percentage_sum": 95,
  "required": 100
}
```

---

## Split Calculator UI

### Features

**Real-time Calculation**
- Show each person's amount as user adjusts splits
- Highlight validation errors immediately
- Running total showing remaining amount

**Quick Actions**
- "Split Equally" button
- "Reset" to clear custom splits
- "Adjust to match" to fix rounding errors

**Visual Feedback**
- Green checkmark when splits are valid
- Red warning when totals don't match
- Show difference amount if invalid

### Example UI Flow

```
Expense: $100.00

Split Type: [Equal] [Unequal] [Shares] [%]

┌─────────────────────────────────────────┐
│ Participant      │ Amount    │ Action   │
├─────────────────────────────────────────┤
│ John Doe         │ $33.34    │ [Edit]   │
│ Jane Smith       │ $33.33    │ [Edit]   │
│ Bob Wilson       │ $33.33    │ [Edit]   │
├─────────────────────────────────────────┤
│ Total            │ $100.00 ✓ │          │
└─────────────────────────────────────────┘
```

---

## Default Split Preferences

### User Story
> As a user, I want my preferred split type to be remembered for convenience.

### Settings
- Default split type per group
- Default split type globally
- Remember last used split type

---

## Split Templates

### User Story
> As a group with recurring expenses, I want to save split configurations.

### Save Template
```json
POST /api/v1/groups/{group_id}/split-templates
{
  "name": "Rent Split",
  "split_type": "percentage",
  "splits": [
    {"user_id": "user-1", "percentage": 50},
    {"user_id": "user-2", "percentage": 30},
    {"user_id": "user-3", "percentage": 20}
  ]
}
```

### Apply Template
```json
POST /api/v1/groups/{group_id}/expenses
{
  "description": "March Rent",
  "amount": 2000.00,
  "template_id": "template-uuid"
}
```

---

## Edge Cases

### Uneven Equal Splits
**Problem**: $100 split 3 ways = $33.33... (infinite decimal)
**Solution**: Distribute remainder cents randomly

### Zero-Sum Payer
**Problem**: Payer paid $100, owes $100 in equal split
**Solution**: Balance = $0, correctly handled

### Single Participant
**Problem**: Expense with only one participant
**Solution**: Allowed - useful for tracking personal expenses in group context

### Very Small Amounts
**Problem**: $0.01 split 4 ways
**Solution**: First participant gets $0.01, others get $0.00

### Very Large Amounts
**Problem**: $999,999.99 max amount
**Solution**: Decimal precision maintained, no overflow

---

## Acceptance Criteria

### Equal Split
- [ ] Divides evenly when divisible
- [ ] Handles remainders correctly
- [ ] All participants owe equal or +1 cent amounts

### Unequal Split
- [ ] User can specify exact amounts
- [ ] Validation ensures total matches
- [ ] Clear error when totals don't match

### Split by Shares
- [ ] Proportional calculation is correct
- [ ] Whole number shares only
- [ ] UI shows calculated amounts

### Split by Percentage
- [ ] Percentages must total 100%
- [ ] Calculated amounts are correct
- [ ] Remainder handling works

### Calculator UI
- [ ] Real-time updates as user types
- [ ] Validation feedback is immediate
- [ ] Quick action buttons work
