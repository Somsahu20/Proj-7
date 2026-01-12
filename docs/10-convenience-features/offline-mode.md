# Offline Mode

## Overview

Users can add expenses while offline. The app syncs automatically when connectivity is restored.

---

## Offline Capabilities

| Feature | Offline Support |
|---------|-----------------|
| View groups | ✅ Cached data |
| View expenses | ✅ Cached data |
| Add expense | ✅ Queued for sync |
| Edit expense | ✅ Queued for sync |
| View balances | ✅ Last known |
| Record payment | ✅ Queued for sync |
| Confirm payment | ❌ Requires connectivity |

---

## Local Storage

### IndexedDB Structure

```javascript
{
  "groups": [...],          // Cached group data
  "expenses": [...],        // Cached expenses
  "pendingActions": [       // Actions to sync
    {
      "id": "local-uuid",
      "type": "create_expense",
      "data": {...},
      "created_at": "2026-01-11T20:00:00Z",
      "status": "pending"
    }
  ],
  "lastSync": "2026-01-11T19:00:00Z"
}
```

---

## Sync Process

### When Online

```
1. Check pending actions
2. For each action:
   a. Send to server
   b. Handle response
   c. Update local data
   d. Mark as synced
3. Fetch latest data
4. Update cache
```

### Conflict Resolution

| Conflict | Resolution |
|----------|------------|
| Same expense edited offline and online | Server version wins, notify user |
| Expense deleted while editing offline | Delete wins, notify user |
| Payment confirmed while editing offline | Server wins, notify user |

---

## User Feedback

### Offline Indicator
- Banner: "You're offline. Changes will sync when connected."
- Pending count badge

### Sync Status
- "Syncing..." with progress
- "All changes synced" confirmation
- Error handling with retry option

---

## Acceptance Criteria

- [ ] Can add expenses offline
- [ ] Pending actions queued
- [ ] Auto-sync on reconnection
- [ ] Conflicts handled gracefully
- [ ] User notified of sync status
