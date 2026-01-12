# User Endpoints

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /users/me | Get current user profile |
| PATCH | /users/me | Update profile |
| POST | /users/me/profile-picture | Upload profile picture |
| DELETE | /users/me/profile-picture | Remove profile picture |
| POST | /users/me/password | Change password |
| POST | /users/me/email/change | Request email change |
| POST | /users/me/email/verify | Verify new email |
| GET | /users/me/notification-preferences | Get notification settings |
| PATCH | /users/me/notification-preferences | Update notification settings |
| DELETE | /users/me | Delete account |

---

## GET /users/me

### Response 200
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "profile_picture": "/uploads/profiles/uuid/photo.jpg",
  "google_id": "google-id",
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-10T15:30:00Z"
}
```

---

## PATCH /users/me

### Request
```json
{
  "name": "John Smith",
  "phone": "+1987654321"
}
```

### Response 200
Updated user object.

---

## POST /users/me/profile-picture

### Request
```
Content-Type: multipart/form-data
file: <image>
```

### Response 200
```json
{
  "profile_picture": "/uploads/profiles/uuid/photo.jpg"
}
```

---

## POST /users/me/password

### Request
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

### Response 200
```json
{
  "message": "Password changed successfully"
}
```

---

## GET /users/me/notification-preferences

### Response 200
```json
{
  "email_enabled": true,
  "digest": {
    "frequency": "weekly",
    "day": "monday",
    "time": "09:00"
  },
  "notifications": {
    "expense_added": true,
    "payment_received": true,
    "...": "..."
  },
  "reminder_settings": {
    "enabled": true,
    "frequency_days": 7,
    "min_amount": 10.00
  }
}
```

---

## PATCH /users/me/notification-preferences

### Request
```json
{
  "notifications": {
    "expense_added": false
  }
}
```

### Response 200
Updated preferences object.

---

## DELETE /users/me

### Request
```json
{
  "password": "password",
  "confirmation": "DELETE MY ACCOUNT"
}
```

### Response 200
```json
{
  "message": "Account scheduled for deletion",
  "deletion_date": "2026-01-25T10:00:00Z"
}
```
