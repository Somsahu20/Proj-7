# Authentication

## Overview

The app supports two authentication methods:
1. **Email/Password** - Traditional registration and login
2. **Google OAuth 2.0** - Social login with Google account

Both methods issue JWT tokens for session management.

---

## Email/Password Authentication

### Signup

#### User Story
> As a new user, I want to create an account with my email and password so that I can access the app.

#### Flow
1. User navigates to signup page
2. User enters email, password, and name
3. System validates input
4. System checks if email already exists
5. System creates user account
6. System sends verification email (optional)
7. User is logged in and redirected to dashboard

#### Technical Requirements

**Request**
```json
POST /api/v1/auth/signup
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Validation Rules**
| Field | Rules |
|-------|-------|
| email | Valid email format, unique, max 255 chars |
| password | Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char |
| name | Min 2 chars, max 100 chars, alphanumeric + spaces |

**Response (Success)**
```json
HTTP 201 Created
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-11T10:00:00Z"
  },
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Validation failed | `{"detail": "Password must be at least 8 characters"}` |
| 409 | Email exists | `{"detail": "Email already registered"}` |

#### Password Hashing
- Algorithm: bcrypt
- Work factor: 12
- Never store plaintext passwords

---

### Login

#### User Story
> As a registered user, I want to log in with my email and password so that I can access my account.

#### Flow
1. User enters email and password
2. System validates credentials
3. System issues JWT tokens
4. Tokens stored in httpOnly cookies
5. User redirected to dashboard

#### Technical Requirements

**Request**
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (Success)**
```json
HTTP 200 OK
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 401 | Invalid credentials | `{"detail": "Invalid email or password"}` |
| 403 | Account disabled | `{"detail": "Account is disabled"}` |

---

### Password Reset

#### User Story
> As a user who forgot my password, I want to reset it via email so that I can regain access to my account.

#### Flow
1. User clicks "Forgot Password"
2. User enters email
3. System sends reset email with token (valid 1 hour)
4. User clicks link in email
5. User enters new password
6. Password updated, user can log in

#### Technical Requirements

**Request Reset**
```json
POST /api/v1/auth/password-reset/request
{
  "email": "user@example.com"
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "If the email exists, a reset link has been sent"
}
```
Note: Always return success to prevent email enumeration.

**Confirm Reset**
```json
POST /api/v1/auth/password-reset/confirm
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!"
}
```

**Response**
```json
HTTP 200 OK
{
  "message": "Password has been reset successfully"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 400 | Invalid/expired token | `{"detail": "Invalid or expired reset token"}` |
| 400 | Weak password | `{"detail": "Password does not meet requirements"}` |

---

## Google OAuth 2.0

### Overview
- OAuth 2.0 Authorization Code flow with PKCE
- Scopes: `openid email profile`
- Auto-create user if first login
- Link Google account to existing email if same

### Flow

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│  User  │────▶│  App   │────▶│ Google │────▶│  App   │
│        │     │/oauth  │     │ Login  │     │Callback│
└────────┘     └────────┘     └────────┘     └────────┘
```

1. User clicks "Login with Google"
2. App redirects to Google OAuth URL
3. User authenticates with Google
4. Google redirects to callback URL with code
5. App exchanges code for tokens
6. App fetches user info from Google
7. App creates/updates user
8. App issues JWT tokens
9. User redirected to dashboard

### Technical Requirements

**Initiate OAuth**
```
GET /api/v1/auth/google
Response: Redirect to Google OAuth URL
```

**OAuth Callback**
```
GET /api/v1/auth/google/callback?code=xxx&state=xxx
Response: Redirect to frontend with tokens in cookies
```

**Environment Variables**
```
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### User Creation from Google
- Extract email, name, profile picture from Google
- Generate random password (user can set later)
- Mark `google_id` for future logins
- Skip email verification (Google verified)

---

## JWT Token Management

### Token Types

| Type | Lifetime | Purpose |
|------|----------|---------|
| Access Token | 15 minutes | API authentication |
| Refresh Token | 7 days | Obtain new access tokens |

### Token Structure

**Access Token Payload**
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "exp": 1704974400,
  "iat": 1704973500,
  "type": "access"
}
```

**Refresh Token Payload**
```json
{
  "sub": "user-uuid",
  "exp": 1705578300,
  "iat": 1704973500,
  "type": "refresh"
}
```

### Token Refresh

**Request**
```json
POST /api/v1/auth/refresh
Cookie: refresh_token=eyJ...
```

**Response**
```json
HTTP 200 OK
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 401 | Invalid/expired refresh token | `{"detail": "Invalid refresh token"}` |
| 401 | User account deleted/disabled | `{"detail": "User no longer exists"}` |

### Token Storage
- Access token: httpOnly cookie or Authorization header
- Refresh token: httpOnly, secure, sameSite=strict cookie
- Never store tokens in localStorage (XSS vulnerable)

---

## Logout

### Flow
1. Clear tokens from cookies
2. Optionally revoke refresh token on server

**Request**
```
POST /api/v1/auth/logout
```

**Response**
```json
HTTP 200 OK
{
  "message": "Logged out successfully"
}
```

---

## Security Considerations

### Rate Limiting
| Endpoint | Limit |
|----------|-------|
| POST /login | 5 attempts per minute per IP |
| POST /signup | 3 per minute per IP |
| POST /password-reset | 3 per hour per email |

### Session Management
- Invalidate all sessions on password change
- Log user out of other devices on request
- Track last login time and IP

### Account Lockout
- Lock account after 5 failed login attempts
- Send email notification on lockout
- Auto-unlock after 30 minutes

---

## Acceptance Criteria

### Signup
- [ ] User can register with valid email/password
- [ ] Duplicate email returns appropriate error
- [ ] Weak password is rejected with clear message
- [ ] User is logged in after successful signup

### Login
- [ ] User can log in with correct credentials
- [ ] Invalid credentials return generic error
- [ ] Successful login sets cookies correctly

### Google OAuth
- [ ] User can initiate Google login
- [ ] New users are created from Google data
- [ ] Existing email users are linked
- [ ] Profile picture is imported from Google

### Password Reset
- [ ] Reset email is sent for valid emails
- [ ] No email enumeration (same response for all)
- [ ] Token expires after 1 hour
- [ ] Password is updated successfully

### Token Management
- [ ] Access token works for protected endpoints
- [ ] Expired access token returns 401
- [ ] Refresh token issues new access token
- [ ] Logout clears all tokens
