# 07. Notifications

This section covers the email notification system, including triggers, templates, and smart reminders.

## Section Contents

| Document | Description |
|----------|-------------|
| [Notification Types](./notification-types.md) | All notification triggers and when they're sent |
| [Email Templates](./email-templates.md) | Email content and formatting |
| [Smart Reminders](./smart-reminders.md) | Pattern-based reminders and intelligent nudges |

## Notification Channels

| Channel | Status |
|---------|--------|
| Email | ✅ Supported |
| In-App | ✅ Supported |
| Push | ❌ Not included |
| SMS | ❌ Not included |

## Core Concepts

### In-App Notifications
- Displayed in notification center
- Real-time via SSE
- Persisted in database
- Can be marked as read

### Email Notifications
- Sent based on user preferences
- Can be instant or batched (digest)
- Include action links
- Have unsubscribe option
