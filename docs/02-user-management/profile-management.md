# Profile Management

## Overview

Users can view and manage their personal information, update their profile picture, and configure account settings.

---

## View Profile

### User Story
> As a user, I want to view my profile information so that I can see what data is stored about me.

### Technical Requirements

**Request**
```
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "profile_picture": "/uploads/profiles/uuid/photo.jpg",
  "google_id": "google-oauth-id",
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-10T15:30:00Z"
}
```

---

## Update Profile

### User Story
> As a user, I want to update my profile information so that my details are accurate.

### Editable Fields

| Field | Validation |
|-------|------------|
| name | 2-100 chars, alphanumeric + spaces |
| phone | E.164 format, optional |

### Technical Requirements

**Request**
```json
PATCH /api/v1/users/me
Authorization: Bearer <access_token>
{
  "name": "John Smith",
  "phone": "+1987654321"
}
```

**Response**
```json
HTTP 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Smith",
  "phone": "+1987654321",
  "profile_picture": "/uploads/profiles/uuid/photo.jpg",
  "updated_at": "2026-01-11T10:00:00Z"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Invalid phone format | `{"detail": "Invalid phone number format"}` |
| 400 | Name too short | `{"detail": "Name must be at least 2 characters"}` |

---

## Update Email

### User Story
> As a user, I want to change my email address so that I can use a different email.

### Flow
1. User submits new email
2. System validates new email is unique
3. System sends verification to new email
4. User clicks verification link
5. Email is updated

### Technical Requirements

**Request Change**
```json
POST /api/v1/users/me/email/change
Authorization: Bearer <access_token>
{
  "new_email": "newemail@example.com",
  "password": "current-password"
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "Verification email sent to newemail@example.com"
}
```

**Verify New Email**
```json
POST /api/v1/users/me/email/verify
{
  "token": "verification-token"
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "Email updated successfully",
  "email": "newemail@example.com"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Email in use | `{"detail": "Email already registered"}` |
| 401 | Wrong password | `{"detail": "Invalid password"}` |
| 400 | Invalid token | `{"detail": "Invalid verification token"}` |

---

## Profile Picture

### Upload Profile Picture

#### User Story
> As a user, I want to upload a profile picture so that others can recognize me.

#### Technical Requirements

**Request**
```
POST /api/v1/users/me/profile-picture
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image file>
```

**Validation**
| Rule | Value |
|------|-------|
| Max file size | 5 MB |
| Allowed types | image/jpeg, image/png, image/webp |
| Max dimensions | 2000x2000 pixels |

**Processing**
- Resize to 400x400 max (maintain aspect ratio)
- Convert to JPEG for consistency
- Store in `/uploads/profiles/{user_id}/`
- Delete old picture if exists

**Response**
```json
HTTP 200 OK
{
  "profile_picture": "/uploads/profiles/uuid/photo.jpg",
  "message": "Profile picture updated"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | File too large | `{"detail": "File size exceeds 5MB limit"}` |
| 400 | Invalid type | `{"detail": "Only JPEG, PNG, and WebP images are allowed"}` |
| 400 | No file | `{"detail": "No file uploaded"}` |

### Delete Profile Picture

**Request**
```
DELETE /api/v1/users/me/profile-picture
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Profile picture removed"
}
```

---

## Change Password

### User Story
> As a user, I want to change my password so that I can keep my account secure.

### Technical Requirements

**Request**
```json
POST /api/v1/users/me/password
Authorization: Bearer <access_token>
{
  "current_password": "OldSecurePass123!",
  "new_password": "NewSecurePass456!"
}
```

**Validation**
- Current password must be correct
- New password must meet strength requirements
- New password must be different from current

**Response**
```json
HTTP 200 OK
{
  "message": "Password changed successfully"
}
```

**Side Effects**
- Invalidate all other sessions
- Send email notification about password change

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 401 | Wrong current password | `{"detail": "Current password is incorrect"}` |
| 400 | Weak new password | `{"detail": "Password does not meet requirements"}` |
| 400 | Same password | `{"detail": "New password must be different"}` |

---

## Account Deletion

### User Story
> As a user, I want to delete my account so that all my data is removed.

### Flow
1. User requests account deletion
2. User confirms with password
3. System schedules deletion (grace period)
4. User receives confirmation email
5. After grace period, data is permanently deleted

### Technical Requirements

**Request**
```json
DELETE /api/v1/users/me
Authorization: Bearer <access_token>
{
  "password": "user-password",
  "confirmation": "DELETE MY ACCOUNT"
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "Account scheduled for deletion",
  "deletion_date": "2026-01-25T10:00:00Z"
}
```

**Grace Period**
- 14 days before permanent deletion
- User can cancel by logging in
- All sessions immediately invalidated
- User marked as `pending_deletion`

**Data Handling**
| Data Type | Action |
|-----------|--------|
| User profile | Delete |
| Group memberships | Remove (don't delete groups) |
| Expenses created by user | Mark as "Deleted User" |
| Payments | Keep for audit trail |
| Files (pictures, receipts) | Delete |

---

## View Transaction History

### User Story
> As a user, I want to see my complete transaction history so that I can track my financial activities.

### Technical Requirements

**Request**
```
GET /api/v1/users/me/transactions
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20, max: 100)
  - type: string (expense | payment | all)
  - start_date: date (optional)
  - end_date: date (optional)
```

**Response**
```json
HTTP 200 OK
{
  "transactions": [
    {
      "id": "uuid",
      "type": "expense",
      "description": "Dinner at restaurant",
      "amount": 50.00,
      "group_id": "uuid",
      "group_name": "Trip to Paris",
      "date": "2026-01-10T20:00:00Z"
    },
    {
      "id": "uuid",
      "type": "payment",
      "description": "Settlement payment",
      "amount": 25.00,
      "from_user": "John",
      "to_user": "Jane",
      "status": "confirmed",
      "date": "2026-01-11T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

## User Preferences

See [Notification Preferences](./notification-preferences.md) for notification settings.

---

## Acceptance Criteria

### View Profile
- [ ] User can view all their profile information
- [ ] Profile picture URL is correct
- [ ] Created and updated timestamps are shown

### Update Profile
- [ ] User can update name
- [ ] User can update phone number
- [ ] Invalid data returns clear error
- [ ] Updated fields reflect immediately

### Email Change
- [ ] Verification email is sent
- [ ] Email only updates after verification
- [ ] Cannot use email that's already registered

### Profile Picture
- [ ] User can upload valid image
- [ ] Image is resized appropriately
- [ ] Invalid files are rejected
- [ ] User can delete profile picture

### Change Password
- [ ] User must provide current password
- [ ] New password must meet requirements
- [ ] Other sessions are logged out
- [ ] Notification email is sent

### Account Deletion
- [ ] User must confirm with password
- [ ] Grace period before permanent deletion
- [ ] User can cancel by logging in
- [ ] All data is properly cleaned up
