# User Models

## UserCreate

```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])', v):
            raise ValueError('Password must contain uppercase, lowercase, number, and special char')
        return v
```

## UserUpdate

```python
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v
```

## UserResponse

```python
class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str]
    profile_picture: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
```

## UserInDB

```python
class UserInDB(UserResponse):
    hashed_password: str
    google_id: Optional[str]
    is_active: bool = True
    is_verified: bool = False
```

## NotificationPreferences

```python
class DigestSettings(BaseModel):
    frequency: Literal['off', 'daily', 'weekly'] = 'off'
    day: Optional[str] = 'monday'
    time: str = '09:00'
    timezone: str = 'UTC'

class ReminderSettings(BaseModel):
    enabled: bool = True
    frequency_days: int = 7
    min_amount: Decimal = Decimal('10.00')

class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    digest: DigestSettings = DigestSettings()
    notifications: dict[str, bool] = {
        'expense_added': True,
        'expense_edited': True,
        'payment_received': True,
        'payment_confirmed': True,
        # ... all notification types
    }
    reminder_settings: ReminderSettings = ReminderSettings()
```

## Token Models

```python
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenPayload(BaseModel):
    sub: UUID
    exp: datetime
    type: Literal['access', 'refresh']
```
