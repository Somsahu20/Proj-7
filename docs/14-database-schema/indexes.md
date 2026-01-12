# Indexes

## Primary Key Indexes
All tables have primary key indexes on `id` (automatically created).

---

## Unique Indexes

```sql
-- Users
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL;

-- Memberships
CREATE UNIQUE INDEX idx_memberships_user_group ON memberships(user_id, group_id);

-- Expense splits
CREATE UNIQUE INDEX idx_splits_expense_user ON expense_splits(expense_id, user_id);

-- Reactions
CREATE UNIQUE INDEX idx_reactions_unique ON reactions(expense_id, user_id, emoji);

-- Invitations
CREATE UNIQUE INDEX idx_invitations_token ON invitations(token);
```

---

## Query Performance Indexes

### Users
```sql
-- For auth lookups
CREATE INDEX idx_users_email_active ON users(email) WHERE is_active = TRUE;

-- For Google OAuth
CREATE INDEX idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL;
```

### Memberships
```sql
-- For listing user's groups
CREATE INDEX idx_memberships_user ON memberships(user_id) WHERE is_active = TRUE;

-- For listing group members
CREATE INDEX idx_memberships_group ON memberships(group_id) WHERE is_active = TRUE;

-- For role checks
CREATE INDEX idx_memberships_role ON memberships(group_id, role) WHERE is_active = TRUE;
```

### Expenses
```sql
-- For listing group expenses
CREATE INDEX idx_expenses_group_date ON expenses(group_id, date DESC) WHERE is_deleted = FALSE;

-- For filtering by category
CREATE INDEX idx_expenses_category ON expenses(group_id, category) WHERE is_deleted = FALSE;

-- For filtering by payer
CREATE INDEX idx_expenses_payer ON expenses(group_id, payer_id) WHERE is_deleted = FALSE;

-- For date range queries
CREATE INDEX idx_expenses_date ON expenses(date DESC) WHERE is_deleted = FALSE;
```

### Expense Splits
```sql
-- For calculating user balances
CREATE INDEX idx_splits_user ON expense_splits(user_id);

-- For expense participant lookups
CREATE INDEX idx_splits_expense ON expense_splits(expense_id);
```

### Payments
```sql
-- For listing group payments
CREATE INDEX idx_payments_group_date ON payments(group_id, date DESC);

-- For user's payment history
CREATE INDEX idx_payments_payer ON payments(payer_id, created_at DESC);
CREATE INDEX idx_payments_receiver ON payments(receiver_id, created_at DESC);

-- For pending confirmations
CREATE INDEX idx_payments_pending ON payments(receiver_id, status) WHERE status = 'pending';

-- For status filtering
CREATE INDEX idx_payments_status ON payments(group_id, status);
```

### Notifications
```sql
-- For user's notifications
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);

-- For unread notifications
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- For notification type filtering
CREATE INDEX idx_notifications_type ON notifications(user_id, type);
```

### Activity Log
```sql
-- For group activity
CREATE INDEX idx_activity_group ON activity_log(group_id, created_at DESC);

-- For user activity
CREATE INDEX idx_activity_user ON activity_log(user_id, created_at DESC);

-- For entity lookups
CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_id);
```

### Comments
```sql
-- For expense comments
CREATE INDEX idx_comments_expense ON comments(expense_id, created_at) WHERE is_deleted = FALSE;

-- For replies
CREATE INDEX idx_comments_parent ON comments(parent_id) WHERE is_deleted = FALSE;
```

### Invitations
```sql
-- For pending invitations
CREATE INDEX idx_invitations_pending ON invitations(group_id, status) WHERE status = 'pending';

-- For email lookups
CREATE INDEX idx_invitations_email ON invitations(email, status);
```

---

## Partial Indexes

```sql
-- Active memberships only
CREATE INDEX idx_memberships_active ON memberships(user_id, group_id) WHERE is_active = TRUE;

-- Non-deleted expenses only
CREATE INDEX idx_expenses_active ON expenses(group_id) WHERE is_deleted = FALSE;

-- Pending payments only
CREATE INDEX idx_payments_pending_only ON payments(receiver_id) WHERE status = 'pending';

-- Unread notifications only
CREATE INDEX idx_notifications_unread_only ON notifications(user_id) WHERE is_read = FALSE;

-- Non-archived groups only
CREATE INDEX idx_groups_active ON groups(id) WHERE is_archived = FALSE AND is_deleted = FALSE;
```

---

## Full-Text Search Indexes

```sql
-- For expense description search
CREATE INDEX idx_expenses_description_search ON expenses
    USING gin(to_tsvector('english', description));

-- For group name search
CREATE INDEX idx_groups_name_search ON groups
    USING gin(to_tsvector('english', name));
```

---

## JSONB Indexes

```sql
-- For notification preferences
CREATE INDEX idx_users_notification_prefs ON users USING gin(notification_preferences);

-- For notification data
CREATE INDEX idx_notifications_data ON notifications USING gin(data);

-- For activity log data
CREATE INDEX idx_activity_data ON activity_log USING gin(data);
```

---

## Index Maintenance

### Recommendations
1. Run `VACUUM ANALYZE` regularly
2. Monitor index usage with `pg_stat_user_indexes`
3. Remove unused indexes
4. Consider partial indexes for common filters
5. Use `CONCURRENTLY` for production index creation

### Example Monitoring Query
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```
