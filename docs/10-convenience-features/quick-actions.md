# Quick Actions

## Overview

Shortcuts and quick actions for common operations.

---

## Quick Actions

### Split Last Transaction

One-tap button to split the most recent expense equally with all group members.

**Flow**:
1. User taps "Split Last"
2. Shows last transaction preview
3. User confirms
4. Expense created with equal split

### Frequent Expenses

Save and reuse common expense templates.

**Request**
```json
POST /api/v1/users/me/expense-templates
{
  "name": "Coffee Run",
  "amount": 15.00,
  "category": "Food & Drinks",
  "split_type": "equal",
  "default_group_id": "uuid"
}
```

**Use Template**
```json
POST /api/v1/groups/{group_id}/expenses/from-template
{
  "template_id": "template-uuid",
  "amount": 18.00  // Optional override
}
```

---

## Dashboard Quick Actions

| Action | Description |
|--------|-------------|
| ➕ Add Expense | Quick add form |
| 💰 Settle Up | Go to settlement |
| 📷 Scan Receipt | Camera + OCR |
| 🎤 Voice Add | Voice input |

---

## Keyboard Shortcuts (Web)

| Shortcut | Action |
|----------|--------|
| `N` | New expense |
| `S` | Settle up |
| `G` | Go to group |
| `?` | Show shortcuts |

---

## Acceptance Criteria

- [ ] Split last works correctly
- [ ] Templates can be saved
- [ ] Templates can be used
- [ ] Dashboard actions work
- [ ] Keyboard shortcuts work (web)
