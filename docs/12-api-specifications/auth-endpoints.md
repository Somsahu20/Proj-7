# Auth Endpoints

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/signup | Register new user |
| POST | /auth/login | Login with email/password |
| POST | /auth/logout | Logout current session |
| POST | /auth/refresh | Refresh access token |
| GET | /auth/google | Initiate Google OAuth |
| GET | /auth/google/callback | Google OAuth callback |
| POST | /auth/password-reset/request | Request password reset |
| POST | /auth/password-reset/confirm | Confirm password reset |

---

## POST /auth/signup

### Request
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

### Response 201
```json
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

### Errors
- 400: Validation error
- 409: Email already exists

---

## POST /auth/login

### Request
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Response 200
```json
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

### Errors
- 401: Invalid credentials

---

## POST /auth/logout

### Request
No body required. Token in Authorization header.

### Response 200
```json
{
  "message": "Logged out successfully"
}
```

---

## POST /auth/refresh

### Request
Refresh token in httpOnly cookie.

### Response 200
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Errors
- 401: Invalid refresh token

---

## GET /auth/google

Redirects to Google OAuth consent screen.

---

## GET /auth/google/callback

Handles OAuth callback, creates/logs in user, redirects to frontend.

---

## POST /auth/password-reset/request

### Request
```json
{
  "email": "user@example.com"
}
```

### Response 200
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

---

## POST /auth/password-reset/confirm

### Request
```json
{
  "token": "reset-token",
  "new_password": "NewSecurePass123!"
}
```

### Response 200
```json
{
  "message": "Password has been reset successfully"
}
```

### Errors
- 400: Invalid/expired token
