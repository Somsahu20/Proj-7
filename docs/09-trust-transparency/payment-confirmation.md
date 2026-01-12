# Payment Confirmation

## Overview

Two-party confirmation ensures both payer and receiver agree that a payment occurred.

---

## Confirmation Flow

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│ Payer  │────▶│Records │────▶│Receiver│────▶│Balances│
│ Pays   │     │Payment │     │Confirms│     │Updated │
│Offline │     │ in App │     │Receipt │     │        │
└────────┘     └────────┘     └────────┘     └────────┘
```

---

## States

| State | Payer Action | Receiver Action | Balance Effect |
|-------|--------------|-----------------|----------------|
| Pending | Can cancel | Must respond | None |
| Confirmed | View only | View only | Updated |
| Rejected | Can dispute | View only | None |
| Cancelled | View only | View only | None |

---

## Time Limits

| Scenario | Limit | Action |
|----------|-------|--------|
| No response | 7 days | Reminder sent |
| No response | 14 days | Second reminder |
| No response | 30 days | Optional auto-confirm (if enabled) |

---

## Both Parties Protected

### Payer Protection
- Proof upload available
- Dispute option if rejected
- Record of payment attempt

### Receiver Protection
- Can reject if not received
- No false payments affect balance
- Clear rejection reasons

---

## Acceptance Criteria

- [ ] Payment requires confirmation
- [ ] Both parties can view status
- [ ] Reminders sent on schedule
- [ ] Dispute available for rejections
- [ ] Proof viewable by both parties
