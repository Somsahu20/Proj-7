# Expense Models

## SplitType Enum

```python
class SplitType(str, Enum):
    EQUAL = 'equal'
    UNEQUAL = 'unequal'
    SHARES = 'shares'
    PERCENTAGE = 'percentage'
```

## SplitInput

```python
class EqualSplitInput(BaseModel):
    participant_ids: list[UUID] = Field(..., min_items=1)

class UnequalSplitInput(BaseModel):
    splits: list[dict]  # [{"user_id": UUID, "amount": Decimal}]

    @validator('splits')
    def validate_splits(cls, v, values):
        # Validate sum equals total
        pass

class SharesSplitInput(BaseModel):
    splits: list[dict]  # [{"user_id": UUID, "shares": int}]

class PercentageSplitInput(BaseModel):
    splits: list[dict]  # [{"user_id": UUID, "percentage": float}]

    @validator('splits')
    def validate_percentage_sum(cls, v):
        total = sum(s['percentage'] for s in v)
        if abs(total - 100) > 0.01:
            raise ValueError('Percentages must total 100%')
        return v
```

## ExpenseCreate

```python
class ExpenseCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    date: date
    payer_id: UUID
    split_type: SplitType
    participant_ids: Optional[list[UUID]] = None  # For equal split
    splits: Optional[list[dict]] = None  # For other splits
    category: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

    @validator('date')
    def date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Date cannot be in the future')
        return v
```

## ExpenseUpdate

```python
class ExpenseUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[date] = None
    payer_id: Optional[UUID] = None
    split_type: Optional[SplitType] = None
    participant_ids: Optional[list[UUID]] = None
    splits: Optional[list[dict]] = None
    category: Optional[str] = None
    notes: Optional[str] = None
```

## SplitResponse

```python
class SplitResponse(BaseModel):
    user_id: UUID
    name: str
    amount: Decimal
    is_payer: bool
    is_settled: bool = False
```

## ExpenseResponse

```python
class ExpenseResponse(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    date: date
    payer: UserResponse
    split_type: SplitType
    splits: list[SplitResponse]
    category: Optional[str]
    category_icon: Optional[str]
    notes: Optional[str]
    receipt_url: Optional[str]
    created_by: UserResponse
    created_at: datetime
    updated_at: Optional[datetime]
    comments_count: int = 0
    reactions: dict = {}
    can_edit: bool
    can_delete: bool

    class Config:
        from_attributes = True
```

## ExpenseListItem

```python
class ExpenseListItem(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    date: date
    payer: UserResponse
    split_type: SplitType
    participant_count: int
    category: Optional[str]
    category_icon: Optional[str]
    has_receipt: bool
    my_share: Decimal
    i_paid: bool
    created_at: datetime
```
