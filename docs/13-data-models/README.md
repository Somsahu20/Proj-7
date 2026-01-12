# 13. Data Models

This section contains Pydantic model specifications for FastAPI.

## Section Contents

| Document | Description |
|----------|-------------|
| [User Models](./user-models.md) | User and profile models |
| [Group Models](./group-models.md) | Group and membership models |
| [Expense Models](./expense-models.md) | Expense and split models |
| [Payment Models](./payment-models.md) | Payment and status models |
| [Notification Models](./notification-models.md) | Notification models |

## Model Patterns

### Base Model
All models extend a common base:

```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
```

### Request vs Response Models
- `*Create` - For creating resources
- `*Update` - For updating (partial)
- `*Response` - For API responses
- `*InDB` - Internal with all fields

### Validation
Using Pydantic validators for:
- Email format
- Password strength
- Amount precision
- Date ranges
