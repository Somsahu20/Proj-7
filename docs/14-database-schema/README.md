# 14. Database Schema

This section contains PostgreSQL database schema specifications.

## Section Contents

| Document | Description |
|----------|-------------|
| [Tables](./tables.md) | All table definitions with columns |
| [Relationships](./relationships.md) | Foreign keys and constraints |
| [Indexes](./indexes.md) | Performance indexes |

## Database Overview

### PostgreSQL Version
PostgreSQL 15+

### Naming Conventions
- Tables: snake_case, plural (e.g., `users`, `expenses`)
- Columns: snake_case
- Primary keys: `id` (UUID)
- Foreign keys: `{table}_id` (e.g., `user_id`)
- Timestamps: `created_at`, `updated_at`

### Common Patterns
- UUIDs for all primary keys
- Soft deletes where appropriate
- Timestamps on all tables
- JSONB for flexible data
