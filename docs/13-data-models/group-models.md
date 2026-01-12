# Group Models

## GroupCategory Enum

```python
class GroupCategory(str, Enum):
    TRIP = 'trip'
    APARTMENT = 'apartment'
    COUPLE = 'couple'
    HOSTEL = 'hostel'
    FRIENDS = 'friends'
    OUTINGS = 'outings'
    PROJECT = 'project'
    FAMILY = 'family'
    OTHER = 'other'
```

## MemberRole Enum

```python
class MemberRole(str, Enum):
    ADMIN = 'admin'
    MEMBER = 'member'
```

## GroupCreate

```python
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: GroupCategory
    invite_emails: Optional[list[EmailStr]] = None
```

## GroupUpdate

```python
class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[GroupCategory] = None
```

## GroupResponse

```python
class GroupResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: GroupCategory
    image_url: Optional[str]
    created_by: UserResponse
    member_count: int
    expense_count: int
    total_expenses: Decimal
    my_role: MemberRole
    my_balance: Decimal
    is_archived: bool = False
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
```

## GroupListItem

```python
class GroupListItem(BaseModel):
    id: UUID
    name: str
    category: GroupCategory
    image_url: Optional[str]
    member_count: int
    my_balance: Decimal
    last_activity: Optional[datetime]
    is_archived: bool = False
```

## MemberResponse

```python
class MemberResponse(BaseModel):
    id: UUID
    name: str
    email: str
    profile_picture: Optional[str]
    role: MemberRole
    balance: Decimal
    joined_at: datetime
```

## InvitationResponse

```python
class InvitationResponse(BaseModel):
    id: UUID
    email: str
    invited_by: str
    invited_at: datetime
    expires_at: datetime
    status: Literal['pending', 'accepted', 'declined', 'expired']
```

## GroupStatistics

```python
class CategoryBreakdown(BaseModel):
    category: str
    amount: Decimal
    count: int
    percentage: float

class MemberBreakdown(BaseModel):
    user_id: UUID
    name: str
    paid: Decimal
    owes: Decimal
    balance: Decimal

class GroupStatistics(BaseModel):
    period: dict
    summary: dict
    by_category: list[CategoryBreakdown]
    by_member: list[MemberBreakdown]
```
