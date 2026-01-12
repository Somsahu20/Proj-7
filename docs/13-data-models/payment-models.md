# Payment Models

## PaymentStatus Enum

```python
class PaymentStatus(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    DISPUTED = 'disputed'
```

## PaymentMethod Enum

```python
class PaymentMethod(str, Enum):
    CASH = 'cash'
    BANK_TRANSFER = 'bank_transfer'
    UPI = 'upi'
    OTHER = 'other'
```

## PaymentCreate

```python
class PaymentCreate(BaseModel):
    receiver_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: Optional[str] = Field(None, max_length=200)
    payment_method: Optional[PaymentMethod] = None
    date: date = Field(default_factory=date.today)
    expense_id: Optional[UUID] = None  # Optional link to expense

    @validator('date')
    def date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Date cannot be in the future')
        return v
```

## PaymentResponse

```python
class PaymentResponse(BaseModel):
    id: UUID
    payer: UserResponse
    receiver: UserResponse
    amount: Decimal
    description: Optional[str]
    payment_method: Optional[PaymentMethod]
    status: PaymentStatus
    date: date
    proof_files: list[dict] = []
    linked_expense: Optional[dict] = None
    created_at: datetime
    confirmed_at: Optional[datetime]
    rejected_at: Optional[datetime]
    rejected_reason: Optional[str]
    cancelled_at: Optional[datetime]
    cancelled_reason: Optional[str]

    class Config:
        from_attributes = True
```

## PaymentListItem

```python
class PaymentListItem(BaseModel):
    id: UUID
    type: Literal['sent', 'received']
    amount: Decimal
    other_party: UserResponse
    group: dict  # {id, name}
    description: Optional[str]
    payment_method: Optional[PaymentMethod]
    status: PaymentStatus
    has_proof: bool
    date: date
    created_at: datetime
    confirmed_at: Optional[datetime]
```

## PaymentReject

```python
class PaymentReject(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)
```

## PaymentCancel

```python
class PaymentCancel(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)
```

## BulkPaymentCreate

```python
class BulkPaymentItem(BaseModel):
    receiver_id: UUID
    amount: Decimal = Field(..., gt=0)
    payment_method: Optional[PaymentMethod] = None

class BulkPaymentCreate(BaseModel):
    payments: list[BulkPaymentItem] = Field(..., min_items=1)
    note: Optional[str] = None
```
