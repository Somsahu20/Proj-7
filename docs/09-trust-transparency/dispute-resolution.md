# Dispute Resolution

## Overview

Members can flag expenses they believe are incorrect, triggering a review process with voting.

---

## Flag Expense

**Request**
```json
POST /api/v1/groups/{group_id}/expenses/{expense_id}/dispute
Authorization: Bearer <access_token>
{
  "reason": "incorrect_amount",
  "description": "The actual bill was $80, not $120",
  "evidence_urls": ["/uploads/disputes/uuid/receipt.jpg"]
}
```

### Dispute Reasons
| Reason | Description |
|--------|-------------|
| `incorrect_amount` | Amount is wrong |
| `incorrect_split` | Split is unfair |
| `not_participant` | I wasn't part of this |
| `duplicate` | This is a duplicate |
| `other` | Other reason |

**Response**
```json
HTTP 201 Created
{
  "dispute_id": "dispute-uuid",
  "status": "open",
  "expense_id": "expense-uuid",
  "flagged_by": {"id": "uuid", "name": "Jane Smith"},
  "reason": "incorrect_amount",
  "created_at": "2026-01-11T21:00:00Z",
  "voting_ends": "2026-01-14T21:00:00Z"
}
```

---

## Voting

### Cast Vote

**Request**
```json
POST /api/v1/groups/{group_id}/disputes/{dispute_id}/vote
{
  "vote": "agree",
  "comment": "I also remember it being less"
}
```

| Vote | Meaning |
|------|---------|
| `agree` | Expense should be corrected |
| `disagree` | Expense is correct |
| `abstain` | No opinion |

### View Votes

**Request**
```
GET /api/v1/groups/{group_id}/disputes/{dispute_id}/votes
```

**Response**
```json
{
  "votes": {
    "agree": 2,
    "disagree": 1,
    "abstain": 1
  },
  "voters": [
    {"user": "Jane", "vote": "agree"},
    {"user": "Bob", "vote": "agree"},
    {"user": "John", "vote": "disagree"},
    {"user": "Alice", "vote": "abstain"}
  ],
  "voting_ends": "2026-01-14T21:00:00Z"
}
```

---

## Resolution

### Auto-Resolution
After voting period (3 days), majority wins:
- More "agree" → Expense flagged for correction
- More "disagree" → Dispute dismissed
- Tie → Escalate to admin

### Admin Resolution

**Request**
```json
POST /api/v1/groups/{group_id}/disputes/{dispute_id}/resolve
Authorization: Bearer <access_token>
{
  "resolution": "correct_expense",
  "action": {
    "new_amount": 80.00
  },
  "notes": "Verified with original receipt"
}
```

---

## Acceptance Criteria

- [ ] Members can flag expenses
- [ ] Evidence can be attached
- [ ] Voting works correctly
- [ ] Auto-resolution after period
- [ ] Admin can override
- [ ] All parties notified
