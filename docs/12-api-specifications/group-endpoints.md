# Group Endpoints

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /groups | List user's groups |
| POST | /groups | Create group |
| GET | /groups/:id | Get group details |
| PATCH | /groups/:id | Update group |
| DELETE | /groups/:id | Delete group |
| GET | /groups/:id/members | List members |
| POST | /groups/:id/members | Add member |
| DELETE | /groups/:id/members/:userId | Remove member |
| PATCH | /groups/:id/members/:userId | Update role |
| POST | /groups/:id/invitations | Send invitations |
| POST | /groups/:id/leave | Leave group |
| GET | /groups/:id/statistics | Get statistics |
| GET | /groups/:id/activity | Get activity log |

---

## GET /groups

### Query Parameters
- status: active | archived | all
- page: int
- limit: int

### Response 200
```json
{
  "groups": [
    {
      "id": "uuid",
      "name": "Trip to Paris",
      "category": "trip",
      "image_url": "/uploads/groups/uuid/image.jpg",
      "member_count": 4,
      "my_balance": -125.50,
      "last_activity": "2026-01-11T10:00:00Z"
    }
  ],
  "pagination": {...}
}
```

---

## POST /groups

### Request
```json
{
  "name": "Trip to Paris",
  "description": "Summer vacation",
  "category": "trip",
  "invite_emails": ["friend@example.com"]
}
```

### Response 201
```json
{
  "id": "uuid",
  "name": "Trip to Paris",
  "category": "trip",
  "member_count": 1,
  "invitations_sent": 1
}
```

---

## GET /groups/:id

### Response 200
```json
{
  "id": "uuid",
  "name": "Trip to Paris",
  "description": "Summer vacation",
  "category": "trip",
  "image_url": "/uploads/groups/uuid/image.jpg",
  "created_by": {...},
  "member_count": 4,
  "expense_count": 25,
  "total_expenses": 1250.50,
  "my_role": "admin",
  "my_balance": -125.50
}
```

---

## GET /groups/:id/members

### Response 200
```json
{
  "members": [
    {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "admin",
      "balance": 287.50,
      "joined_at": "2026-01-01T10:00:00Z"
    }
  ],
  "pending_invitations": [...]
}
```

---

## POST /groups/:id/invitations

### Request
```json
{
  "emails": ["friend1@example.com", "friend2@example.com"]
}
```

### Response 200
```json
{
  "results": [
    {"email": "friend1@example.com", "status": "invited"},
    {"email": "friend2@example.com", "status": "already_member"}
  ]
}
```

---

## GET /groups/:id/statistics

### Response 200
```json
{
  "period": {...},
  "summary": {
    "total_expenses": 1250.50,
    "expense_count": 25
  },
  "by_category": [...],
  "by_member": [...]
}
```
