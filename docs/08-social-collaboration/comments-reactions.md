# Comments & Reactions

## Overview

Users can comment on expenses and react with emojis to provide feedback and context.

---

## Comments

### Add Comment

**Request**
```json
POST /api/v1/groups/{group_id}/expenses/{expense_id}/comments
Authorization: Bearer <access_token>
{
  "content": "Great choice for dinner! The pasta was amazing.",
  "mentions": ["user-uuid-1", "user-uuid-2"]
}
```

**Validation**
| Rule | Value |
|------|-------|
| content | 1-500 chars |
| mentions | Must be group members |

**Response**
```json
HTTP 201 Created
{
  "id": "comment-uuid",
  "content": "Great choice for dinner! The pasta was amazing.",
  "author": {
    "id": "user-uuid",
    "name": "Jane Smith",
    "profile_picture": "/uploads/profiles/uuid/photo.jpg"
  },
  "mentions": [
    {"id": "user-uuid-1", "name": "John Doe"},
    {"id": "user-uuid-2", "name": "Bob Wilson"}
  ],
  "created_at": "2026-01-11T21:00:00Z"
}
```

### View Comments

**Request**
```
GET /api/v1/groups/{group_id}/expenses/{expense_id}/comments
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "comments": [
    {
      "id": "comment-uuid-1",
      "content": "Great choice for dinner!",
      "author": {"id": "uuid", "name": "Jane Smith"},
      "created_at": "2026-01-11T21:00:00Z",
      "replies": [
        {
          "id": "comment-uuid-2",
          "content": "Agreed! Let's go there again.",
          "author": {"id": "uuid", "name": "Bob Wilson"},
          "created_at": "2026-01-11T21:30:00Z"
        }
      ]
    }
  ],
  "total": 2
}
```

### Reply to Comment

**Request**
```json
POST /api/v1/groups/{group_id}/expenses/{expense_id}/comments/{comment_id}/replies
{
  "content": "Agreed! Let's go there again."
}
```

### Edit Comment

**Request**
```json
PATCH /api/v1/groups/{group_id}/expenses/{expense_id}/comments/{comment_id}
{
  "content": "Great choice for dinner! The pasta was amazing. 🍝"
}
```

Only the author can edit within 24 hours.

### Delete Comment

**Request**
```
DELETE /api/v1/groups/{group_id}/expenses/{expense_id}/comments/{comment_id}
```

Only the author or group admin can delete.

---

## Mentions

### @Mention Syntax

In comment content: `@[John Doe](user-uuid)`

Frontend converts display names to this format before sending.

### Mention Notifications

When mentioned, user receives:
- In-app notification
- Email (if enabled)

**Notification**:
```
{author} mentioned you in a comment on "{expense_description}"
"{comment_preview}..."
```

---

## Reactions

### Available Reactions

| Emoji | Meaning |
|-------|---------|
| 👍 | Like / Approve |
| ❤️ | Love |
| 😂 | Funny |
| 😮 | Surprised |
| 😢 | Sad |
| 🎉 | Celebration |

### Add Reaction

**Request**
```json
POST /api/v1/groups/{group_id}/expenses/{expense_id}/reactions
{
  "emoji": "👍"
}
```

**Response**
```json
HTTP 201 Created
{
  "emoji": "👍",
  "user": {"id": "uuid", "name": "Jane Smith"},
  "created_at": "2026-01-11T21:00:00Z"
}
```

### Remove Reaction

**Request**
```
DELETE /api/v1/groups/{group_id}/expenses/{expense_id}/reactions/{emoji}
```

### View Reactions

**Request**
```
GET /api/v1/groups/{group_id}/expenses/{expense_id}/reactions
```

**Response**
```json
HTTP 200 OK
{
  "reactions": {
    "👍": {
      "count": 3,
      "users": [
        {"id": "uuid-1", "name": "Jane Smith"},
        {"id": "uuid-2", "name": "Bob Wilson"},
        {"id": "uuid-3", "name": "Alice Brown"}
      ],
      "reacted_by_me": true
    },
    "😂": {
      "count": 1,
      "users": [{"id": "uuid-4", "name": "John Doe"}],
      "reacted_by_me": false
    }
  },
  "total": 4
}
```

---

## Acceptance Criteria

### Comments
- [ ] Can add comment to expense
- [ ] Can reply to comment
- [ ] Can edit own comment
- [ ] Can delete own comment
- [ ] Admin can delete any comment

### Mentions
- [ ] @mention syntax works
- [ ] Mentioned users notified
- [ ] Only group members can be mentioned

### Reactions
- [ ] Can add reaction
- [ ] Can remove reaction
- [ ] Reaction counts accurate
- [ ] Shows who reacted
