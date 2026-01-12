# Member Management

## Overview

Group admins can manage members by inviting new people, removing existing members, and managing roles. All members can view the member list and their roles.

---

## Member Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full access: manage members, edit group, delete group |
| `member` | Add expenses, record payments, view all data |

### Role Capabilities

| Action | Admin | Member |
|--------|-------|--------|
| Add expenses | ✅ | ✅ |
| Edit own expenses | ✅ | ✅ |
| Delete own expenses | ✅ | ✅ |
| Edit others' expenses | ✅ | ❌ |
| Delete others' expenses | ✅ | ❌ |
| Record payments | ✅ | ✅ |
| Approve payments | ✅ | ✅ (for payments to them) |
| Invite members | ✅ | ❌ |
| Remove members | ✅ | ❌ |
| Change roles | ✅ | ❌ |
| Edit group settings | ✅ | ❌ |
| Delete group | ✅ | ❌ |

---

## View Members

### User Story
> As a group member, I want to see all members and their roles so I know who is in the group.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/members
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "members": [
    {
      "id": "user-uuid-1",
      "name": "John Doe",
      "email": "john@example.com",
      "profile_picture": "/uploads/profiles/uuid/photo.jpg",
      "role": "admin",
      "joined_at": "2026-01-01T10:00:00Z",
      "balance": -25.50
    },
    {
      "id": "user-uuid-2",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "profile_picture": null,
      "role": "member",
      "joined_at": "2026-01-05T14:00:00Z",
      "balance": 25.50
    }
  ],
  "pending_invitations": [
    {
      "email": "pending@example.com",
      "invited_at": "2026-01-10T10:00:00Z",
      "invited_by": "John Doe",
      "expires_at": "2026-01-17T10:00:00Z"
    }
  ],
  "total_members": 2,
  "total_pending": 1
}
```

---

## Invite Members

### User Story
> As a group admin, I want to invite people to the group so they can participate in expense tracking.

### Invitation Methods

1. **By Email** - Send invitation to email address
2. **By Username** - Add existing user directly

### Invite by Email

**Request**
```json
POST /api/v1/groups/{group_id}/invitations
Authorization: Bearer <access_token>
{
  "emails": ["friend1@example.com", "friend2@example.com"]
}
```

**Response**
```json
HTTP 200 OK
{
  "results": [
    {
      "email": "friend1@example.com",
      "status": "invited",
      "message": "Invitation sent"
    },
    {
      "email": "friend2@example.com",
      "status": "already_member",
      "message": "User is already a member"
    }
  ]
}
```

**Statuses**
| Status | Description |
|--------|-------------|
| `invited` | Invitation email sent |
| `already_member` | User is already in the group |
| `already_invited` | Pending invitation exists |
| `invalid_email` | Email format is invalid |

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not admin | `{"detail": "Only admins can invite members"}` |
| 400 | No valid emails | `{"detail": "No valid emails provided"}` |

### Invitation Email Content
- Group name and description
- Inviter's name
- Link to accept invitation
- Link to decline invitation
- Expiration notice (7 days)

---

## Accept/Decline Invitation

### Accept Invitation

**For Logged-in Users**
```json
POST /api/v1/groups/{group_id}/invitations/accept
Authorization: Bearer <access_token>
```

**For Non-Users (via email link)**
```
GET /api/v1/invitations/accept?token=xxx
→ Redirect to signup page with invitation context
```

**Response**
```json
HTTP 200 OK
{
  "message": "You have joined the group",
  "group": {
    "id": "uuid",
    "name": "Trip to Paris"
  }
}
```

### Decline Invitation

**Request**
```json
POST /api/v1/groups/{group_id}/invitations/decline
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Invitation declined"
}
```

---

## Add Member Directly

### User Story
> As a group admin, I want to add an existing user directly to the group.

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/members
Authorization: Bearer <access_token>
{
  "user_id": "user-uuid",
  "role": "member"
}
```

**Response**
```json
HTTP 201 Created
{
  "id": "user-uuid",
  "name": "Jane Smith",
  "role": "member",
  "joined_at": "2026-01-11T10:00:00Z"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not admin | `{"detail": "Only admins can add members"}` |
| 404 | User not found | `{"detail": "User not found"}` |
| 409 | Already member | `{"detail": "User is already a member"}` |

---

## Remove Member

### User Story
> As a group admin, I want to remove a member from the group.

### Technical Requirements

**Request**
```
DELETE /api/v1/groups/{group_id}/members/{user_id}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Member removed from group"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not admin | `{"detail": "Only admins can remove members"}` |
| 400 | Has unsettled balance | `{"detail": "Member has unsettled balance of $25.50"}` |
| 400 | Removing self as only admin | `{"detail": "Cannot remove yourself as the only admin"}` |
| 404 | Member not found | `{"detail": "Member not found in group"}` |

### Pre-removal Check
- Check if member has outstanding balance
- If balance exists, must be settled first
- Or admin can choose to forgive the balance

### Side Effects
- Member loses access to group
- Member's expenses remain (attributed to "Former Member")
- Member receives notification
- Activity logged

---

## Leave Group

### User Story
> As a group member, I want to leave a group I no longer want to be part of.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/leave
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "You have left the group"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Has unsettled balance | `{"detail": "You have an unsettled balance of $25.50"}` |
| 400 | Only admin | `{"detail": "You must transfer admin role before leaving"}` |

---

## Change Member Role

### User Story
> As a group admin, I want to change a member's role to give them more or fewer permissions.

### Technical Requirements

**Request**
```json
PATCH /api/v1/groups/{group_id}/members/{user_id}
Authorization: Bearer <access_token>
{
  "role": "admin"
}
```

**Response**
```json
HTTP 200 OK
{
  "id": "user-uuid",
  "name": "Jane Smith",
  "role": "admin",
  "message": "Role updated successfully"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not admin | `{"detail": "Only admins can change roles"}` |
| 400 | Demoting only admin | `{"detail": "Cannot demote the only admin"}` |

---

## Transfer Admin Role

### User Story
> As the group admin, I want to transfer admin privileges to another member before leaving.

### Technical Requirements

**Request**
```json
POST /api/v1/groups/{group_id}/transfer-admin
Authorization: Bearer <access_token>
{
  "new_admin_id": "user-uuid"
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "Admin role transferred to Jane Smith",
  "new_admin": {
    "id": "user-uuid",
    "name": "Jane Smith"
  }
}
```

**Side Effects**
- Current user becomes regular member
- New admin receives notification
- Activity logged

---

## Cancel Pending Invitation

### User Story
> As a group admin, I want to cancel a pending invitation.

### Technical Requirements

**Request**
```
DELETE /api/v1/groups/{group_id}/invitations/{invitation_id}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Invitation cancelled"
}
```

---

## Resend Invitation

### User Story
> As a group admin, I want to resend an invitation to someone who didn't respond.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/invitations/{invitation_id}/resend
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Invitation resent",
  "expires_at": "2026-01-18T10:00:00Z"
}
```

Note: Resets expiration to 7 days from now.

---

## Acceptance Criteria

### View Members
- [ ] All members are displayed with roles
- [ ] Pending invitations are shown
- [ ] Member balances are visible
- [ ] Profile pictures are displayed

### Invite Members
- [ ] Admin can invite via email
- [ ] Multiple emails can be invited at once
- [ ] Invitation email is sent
- [ ] Duplicate invitations are handled

### Accept/Decline
- [ ] Existing users can accept from notification
- [ ] New users can signup and join
- [ ] Decline removes the invitation
- [ ] Expired invitations are rejected

### Remove Member
- [ ] Admin can remove members
- [ ] Members with balance cannot be removed
- [ ] Removed member loses access
- [ ] Notification is sent

### Leave Group
- [ ] Member can leave voluntarily
- [ ] Cannot leave with unsettled balance
- [ ] Admin must transfer role first

### Role Management
- [ ] Admin can promote to admin
- [ ] Admin can demote to member
- [ ] Cannot have zero admins
- [ ] Role changes are logged
