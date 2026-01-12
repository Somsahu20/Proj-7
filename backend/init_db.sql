-- Create database
-- Run this command in psql: CREATE DATABASE moneybyte;

-- The tables are automatically created by SQLAlchemy when the app starts.
-- This file contains additional indexes and optimizations.

-- Performance Indexes (run after initial table creation)

-- Users
CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email) WHERE is_active = TRUE;

-- Memberships
CREATE INDEX IF NOT EXISTS idx_memberships_user ON memberships(user_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_memberships_group ON memberships(group_id) WHERE is_active = TRUE;

-- Expenses
CREATE INDEX IF NOT EXISTS idx_expenses_group_date ON expenses(group_id, date DESC) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_expenses_payer ON expenses(group_id, payer_id) WHERE is_deleted = FALSE;

-- Expense Splits
CREATE INDEX IF NOT EXISTS idx_splits_user ON expense_splits(user_id);
CREATE INDEX IF NOT EXISTS idx_splits_expense ON expense_splits(expense_id);

-- Payments
CREATE INDEX IF NOT EXISTS idx_payments_group_date ON payments(group_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_payments_pending ON payments(receiver_id, status) WHERE status = 'pending';

-- Notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- Activity Log
CREATE INDEX IF NOT EXISTS idx_activity_group ON activity_log(group_id, created_at DESC);

-- Comments
CREATE INDEX IF NOT EXISTS idx_comments_expense ON comments(expense_id, created_at) WHERE is_deleted = FALSE;

-- Invitations
CREATE INDEX IF NOT EXISTS idx_invitations_pending ON invitations(group_id, status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_invitations_email ON invitations(email, status) WHERE status = 'pending';

-- Friendships
CREATE INDEX IF NOT EXISTS idx_friendships_requester ON friendships(requester_id, status);
CREATE INDEX IF NOT EXISTS idx_friendships_addressee ON friendships(addressee_id, status);
CREATE INDEX IF NOT EXISTS idx_friendships_accepted ON friendships(status) WHERE status = 'accepted';

-- Groups - friend groups
CREATE INDEX IF NOT EXISTS idx_groups_friend ON groups(is_friend_group) WHERE is_friend_group = TRUE;
