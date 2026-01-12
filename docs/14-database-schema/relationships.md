# Relationships

## Entity Relationship Diagram

```
┌─────────┐       ┌────────────┐       ┌─────────┐
│  users  │◀─────▶│memberships │◀─────▶│ groups  │
└────┬────┘       └────────────┘       └────┬────┘
     │                                      │
     │            ┌─────────────┐           │
     └───────────▶│  expenses   │◀──────────┘
                  └──────┬──────┘
                         │
                  ┌──────┴──────┐
                  ▼             ▼
            ┌──────────┐  ┌──────────┐
            │  splits  │  │ comments │
            └──────────┘  └──────────┘
                  │
                  ▼
            ┌──────────┐
            │ payments │
            └──────────┘
```

---

## Foreign Key Constraints

### users
None (root entity)

### groups
```sql
ALTER TABLE groups
    ADD CONSTRAINT fk_groups_created_by
    FOREIGN KEY (created_by_id) REFERENCES users(id);
```

### memberships
```sql
ALTER TABLE memberships
    ADD CONSTRAINT fk_memberships_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE memberships
    ADD CONSTRAINT fk_memberships_group
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE;

ALTER TABLE memberships
    ADD CONSTRAINT fk_memberships_invited_by
    FOREIGN KEY (invited_by_id) REFERENCES users(id);
```

### expenses
```sql
ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_group
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE;

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_payer
    FOREIGN KEY (payer_id) REFERENCES users(id);

ALTER TABLE expenses
    ADD CONSTRAINT fk_expenses_created_by
    FOREIGN KEY (created_by_id) REFERENCES users(id);
```

### expense_splits
```sql
ALTER TABLE expense_splits
    ADD CONSTRAINT fk_splits_expense
    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE;

ALTER TABLE expense_splits
    ADD CONSTRAINT fk_splits_user
    FOREIGN KEY (user_id) REFERENCES users(id);
```

### payments
```sql
ALTER TABLE payments
    ADD CONSTRAINT fk_payments_group
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE;

ALTER TABLE payments
    ADD CONSTRAINT fk_payments_payer
    FOREIGN KEY (payer_id) REFERENCES users(id);

ALTER TABLE payments
    ADD CONSTRAINT fk_payments_receiver
    FOREIGN KEY (receiver_id) REFERENCES users(id);

ALTER TABLE payments
    ADD CONSTRAINT fk_payments_expense
    FOREIGN KEY (expense_id) REFERENCES expenses(id);
```

### notifications
```sql
ALTER TABLE notifications
    ADD CONSTRAINT fk_notifications_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

### comments
```sql
ALTER TABLE comments
    ADD CONSTRAINT fk_comments_expense
    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE;

ALTER TABLE comments
    ADD CONSTRAINT fk_comments_user
    FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE comments
    ADD CONSTRAINT fk_comments_parent
    FOREIGN KEY (parent_id) REFERENCES comments(id);
```

---

## Check Constraints

### payments
```sql
ALTER TABLE payments
    ADD CONSTRAINT chk_payments_different_users
    CHECK (payer_id != receiver_id);

ALTER TABLE payments
    ADD CONSTRAINT chk_payments_positive_amount
    CHECK (amount > 0);

ALTER TABLE payments
    ADD CONSTRAINT chk_payments_status
    CHECK (status IN ('pending', 'confirmed', 'rejected', 'cancelled', 'disputed'));
```

### expenses
```sql
ALTER TABLE expenses
    ADD CONSTRAINT chk_expenses_positive_amount
    CHECK (amount > 0);

ALTER TABLE expenses
    ADD CONSTRAINT chk_expenses_split_type
    CHECK (split_type IN ('equal', 'unequal', 'shares', 'percentage'));
```

### memberships
```sql
ALTER TABLE memberships
    ADD CONSTRAINT chk_memberships_role
    CHECK (role IN ('admin', 'member'));
```

---

## Unique Constraints

```sql
-- One membership per user per group
ALTER TABLE memberships
    ADD CONSTRAINT uq_memberships_user_group
    UNIQUE (user_id, group_id);

-- One split per user per expense
ALTER TABLE expense_splits
    ADD CONSTRAINT uq_splits_expense_user
    UNIQUE (expense_id, user_id);

-- One reaction type per user per expense
ALTER TABLE reactions
    ADD CONSTRAINT uq_reactions_expense_user_emoji
    UNIQUE (expense_id, user_id, emoji);

-- One vote per user per dispute
ALTER TABLE dispute_votes
    ADD CONSTRAINT uq_dispute_votes_user
    UNIQUE (dispute_id, user_id);
```

---

## Cascade Behavior

| Parent | Child | On Delete |
|--------|-------|-----------|
| users | memberships | CASCADE |
| users | notifications | CASCADE |
| groups | memberships | CASCADE |
| groups | expenses | CASCADE |
| groups | payments | CASCADE |
| expenses | expense_splits | CASCADE |
| expenses | comments | CASCADE |
| expenses | reactions | CASCADE |
| payments | payment_proofs | CASCADE |
| disputes | dispute_votes | CASCADE |
