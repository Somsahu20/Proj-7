# Group Creation

## Overview

Users can create groups to track shared expenses with friends, roommates, travel companions, or any other group of people.

---

## Create Group

### User Story
> As a user, I want to create a new group so that I can track shared expenses with others.

### Group Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Group name (3-100 chars) |
| description | string | No | Optional description (max 500 chars) |
| image | file | No | Group image/avatar |
| category | enum | Yes | Type of group |

### Group Categories

| Category | Description | Icon Suggestion |
|----------|-------------|-----------------|
| `trip` | Travel and vacation expenses | ✈️ |
| `apartment` | Rent, utilities, shared living | 🏠 |
| `couple` | Expenses between partners | ❤️ |
| `hostel` | Hostel/dorm shared expenses | 🛏️ |
| `friends` | General friend group | 👥 |
| `outings` | Restaurants, events, activities | 🎉 |
| `project` | Work or project-related | 💼 |
| `family` | Family expenses | 👨‍👩‍👧‍👦 |
| `other` | Miscellaneous | 📁 |

### Technical Requirements

**Request**
```json
POST /api/v1/groups
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "name": "Trip to Paris",
  "description": "Our summer vacation to Paris",
  "category": "trip",
  "image": <file> (optional)
}
```

**Validation**
| Field | Rules |
|-------|-------|
| name | 3-100 chars, not empty, trimmed |
| description | Max 500 chars |
| category | Must be valid category enum |
| image | Max 2MB, jpeg/png/webp |

**Response (Success)**
```json
HTTP 201 Created
{
  "id": "uuid",
  "name": "Trip to Paris",
  "description": "Our summer vacation to Paris",
  "category": "trip",
  "image_url": "/uploads/groups/uuid/image.jpg",
  "created_by": {
    "id": "user-uuid",
    "name": "John Doe"
  },
  "member_count": 1,
  "created_at": "2026-01-11T10:00:00Z"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Name too short | `{"detail": "Group name must be at least 3 characters"}` |
| 400 | Invalid category | `{"detail": "Invalid category"}` |
| 400 | Image too large | `{"detail": "Image size exceeds 2MB limit"}` |

### Side Effects
- Creator is added as member with `admin` role
- Group activity logged
- No notifications (creator is only member)

---

## Create Group with Initial Members

### User Story
> As a user, I want to create a group and invite members at the same time for convenience.

### Technical Requirements

**Request**
```json
POST /api/v1/groups
Authorization: Bearer <access_token>
{
  "name": "Apartment 4B",
  "category": "apartment",
  "invite_emails": [
    "roommate1@example.com",
    "roommate2@example.com"
  ]
}
```

**Response**
```json
HTTP 201 Created
{
  "id": "uuid",
  "name": "Apartment 4B",
  "category": "apartment",
  "member_count": 1,
  "invitations_sent": 2,
  "created_at": "2026-01-11T10:00:00Z"
}
```

### Invitation Behavior
- If user exists with email → send in-app + email notification
- If user doesn't exist → send email invitation to join app
- Invitations expire after 7 days
- Invited users can decline

---

## Group Defaults by Category

Different categories can have default settings:

| Category | Default Split | Typical Expense Categories |
|----------|---------------|---------------------------|
| trip | Equal | Transport, Accommodation, Food, Activities |
| apartment | Equal | Rent, Utilities, Groceries, Supplies |
| couple | Equal | Dining, Entertainment, Groceries, Gifts |
| outings | Equal | Food, Drinks, Tickets, Transport |

---

## Quick Create Templates

### User Story
> As a user, I want to quickly create groups from templates for common scenarios.

### Available Templates

**Trip Template**
```json
{
  "category": "trip",
  "default_expense_categories": [
    "Transport",
    "Accommodation",
    "Food & Drinks",
    "Activities",
    "Shopping",
    "Other"
  ]
}
```

**Apartment Template**
```json
{
  "category": "apartment",
  "default_expense_categories": [
    "Rent",
    "Utilities",
    "Internet",
    "Groceries",
    "Cleaning Supplies",
    "Other"
  ]
}
```

---

## Group Image

### Upload Group Image

**Request**
```
POST /api/v1/groups/{group_id}/image
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image file>
```

**Validation**
| Rule | Value |
|------|-------|
| Max size | 2 MB |
| Allowed types | image/jpeg, image/png, image/webp |
| Dimensions | Resized to 400x400 max |

**Response**
```json
HTTP 200 OK
{
  "image_url": "/uploads/groups/uuid/image.jpg"
}
```

### Remove Group Image

**Request**
```
DELETE /api/v1/groups/{group_id}/image
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Group image removed"
}
```

---

## Acceptance Criteria

### Basic Creation
- [ ] User can create group with name and category
- [ ] Optional description is saved
- [ ] Creator becomes admin automatically
- [ ] Group appears in creator's group list

### Categories
- [ ] All category options are available
- [ ] Category affects default settings
- [ ] Category icon/color is displayed

### Image
- [ ] User can upload group image
- [ ] Image is resized appropriately
- [ ] Invalid images are rejected
- [ ] User can remove group image

### Initial Invitations
- [ ] User can invite members during creation
- [ ] Existing users receive notification
- [ ] Non-users receive email invitation
- [ ] Invalid emails are handled gracefully
