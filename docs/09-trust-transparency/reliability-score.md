# Reliability Score

## Overview

A private score that tracks payment punctuality to help users understand their payment patterns.

---

## Score Calculation

### Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| On-time payments | 40% | Payments within 7 days |
| Response time | 30% | Time to confirm payments |
| Settlement rate | 20% | % of debts settled |
| Dispute rate | 10% | Low disputes = better |

### Score Range

| Range | Label | Description |
|-------|-------|-------------|
| 90-100 | Excellent | Consistently prompt |
| 70-89 | Good | Generally reliable |
| 50-69 | Fair | Some delays |
| 0-49 | Needs Improvement | Frequent delays |

---

## View My Score

**Request**
```
GET /api/v1/users/me/reliability-score
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "score": 85,
  "label": "Good",
  "breakdown": {
    "on_time_payments": 90,
    "response_time": 80,
    "settlement_rate": 85,
    "dispute_rate": 95
  },
  "trend": "improving",
  "tips": [
    "Confirm payment requests within 24 hours to improve your score"
  ]
}
```

---

## Privacy

- Score is **private** (only visible to user)
- No public rankings
- Not shared with group members
- Used for self-improvement only

---

## Acceptance Criteria

- [ ] Score calculated accurately
- [ ] All factors considered
- [ ] Trend tracking works
- [ ] Tips are helpful
- [ ] Completely private
