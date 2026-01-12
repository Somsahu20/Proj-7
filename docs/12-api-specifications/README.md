# 12. API Specifications

This section contains detailed REST API endpoint specifications.

## Section Contents

| Document | Description |
|----------|-------------|
| [Auth Endpoints](./auth-endpoints.md) | Authentication and authorization |
| [User Endpoints](./user-endpoints.md) | User profile management |
| [Group Endpoints](./group-endpoints.md) | Group CRUD and members |
| [Expense Endpoints](./expense-endpoints.md) | Expense CRUD and splits |
| [Payment Endpoints](./payment-endpoints.md) | Payment recording and approval |
| [Balance Endpoints](./balance-endpoints.md) | Balance calculations |
| [Notification Endpoints](./notification-endpoints.md) | Notification management |
| [SSE Events](./sse-events.md) | Real-time event specifications |

## API Overview

### Base URL
```
https://api.example.com/api/v1
```

### Authentication
All endpoints except auth require Bearer token:
```
Authorization: Bearer <access_token>
```

### Response Format
```json
{
  "data": {...},
  "message": "Success",
  "timestamp": "2026-01-11T10:00:00Z"
}
```

### Error Format
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-11T10:00:00Z"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Server Error |
