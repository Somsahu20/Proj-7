from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import os
import uuid
import aiofiles

from app.db.database import get_db
from app.api.deps import get_current_user
from app.core.config import settings
from app.models import User, Group, Membership, Expense, ExpenseSplit
from app.schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse,
    SplitResponse, UserResponse, ExpenseTemplateCreate, ExpenseTemplateResponse
)
from app.models import ExpenseTemplate

router = APIRouter(prefix="/expenses", tags=["Expenses"])


async def check_group_membership(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID) -> Membership:
    """Check if user is a member of the group."""
    result = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == user_id,
                Membership.is_active == True
            )
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    return membership


def calculate_splits(
    amount: Decimal,
    split_type: str,
    participant_ids: List[uuid.UUID],
    splits_data: List[dict]
) -> List[dict]:
    """Calculate split amounts based on split type."""
    if split_type == "equal":
        per_person = amount / len(participant_ids)
        return [{"user_id": uid, "amount": per_person} for uid in participant_ids]

    elif split_type == "unequal":
        # Splits provided directly with amounts
        total = sum(s.get("amount", 0) for s in splits_data)
        if abs(total - amount) > Decimal("0.01"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Split amounts ({total}) don't equal expense amount ({amount})"
            )
        return splits_data

    elif split_type == "shares":
        # Calculate based on shares
        total_shares = sum(s.get("shares", 1) for s in splits_data)
        per_share = amount / total_shares
        return [
            {
                "user_id": s["user_id"],
                "amount": per_share * s.get("shares", 1),
                "shares": s.get("shares", 1)
            }
            for s in splits_data
        ]

    elif split_type == "percentage":
        # Calculate based on percentages
        total_pct = sum(s.get("percentage", 0) for s in splits_data)
        if abs(total_pct - 100) > Decimal("0.01"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Percentages ({total_pct}%) don't equal 100%"
            )
        return [
            {
                "user_id": s["user_id"],
                "amount": amount * s.get("percentage", 0) / 100,
                "percentage": s.get("percentage", 0)
            }
            for s in splits_data
        ]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid split type: {split_type}"
    )


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new expense."""
    await check_group_membership(db, data.group_id, current_user.id)

    # Create expense
    expense = Expense(
        group_id=data.group_id,
        description=data.description,
        amount=data.amount,
        date=data.date,
        payer_id=data.payer_id,
        split_type=data.split_type,
        category=data.category,
        notes=data.notes,
        created_by_id=current_user.id,
    )
    db.add(expense)
    await db.flush()

    # Calculate and create splits
    if data.split_type == "equal" and data.participant_ids:
        splits_data = calculate_splits(
            data.amount, "equal", data.participant_ids, []
        )
    else:
        splits_data = calculate_splits(
            data.amount,
            data.split_type,
            [s.user_id for s in data.splits],
            [s.model_dump() for s in data.splits]
        )

    for split_info in splits_data:
        split = ExpenseSplit(
            expense_id=expense.id,
            user_id=split_info["user_id"],
            amount=split_info["amount"],
            shares=split_info.get("shares"),
            percentage=split_info.get("percentage"),
        )
        db.add(split)

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(Expense)
        .options(
            selectinload(Expense.payer),
            selectinload(Expense.splits).selectinload(ExpenseSplit.user)
        )
        .where(Expense.id == expense.id)
    )
    expense = result.scalar_one()

    return ExpenseResponse(
        **expense.__dict__,
        payer=UserResponse.model_validate(expense.payer),
        splits=[
            SplitResponse(**s.__dict__, user=UserResponse.model_validate(s.user))
            for s in expense.splits
        ]
    )


@router.get("", response_model=ExpenseListResponse)
async def list_expenses(
    group_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    payer_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List expenses for a group with filtering."""
    await check_group_membership(db, group_id, current_user.id)

    # Build query
    query = select(Expense).where(
        and_(
            Expense.group_id == group_id,
            Expense.is_deleted == False
        )
    )

    if category:
        query = query.where(Expense.category == category)
    if payer_id:
        query = query.where(Expense.payer_id == payer_id)
    if start_date:
        query = query.where(Expense.date >= start_date)
    if end_date:
        query = query.where(Expense.date <= end_date)
    if search:
        query = query.where(Expense.description.ilike(f"%{search}%"))

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    # Get paginated results
    query = query.options(
        selectinload(Expense.payer),
        selectinload(Expense.splits).selectinload(ExpenseSplit.user)
    ).order_by(Expense.date.desc(), Expense.created_at.desc())

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    expenses = result.scalars().all()

    return ExpenseListResponse(
        expenses=[
            ExpenseResponse(
                **e.__dict__,
                payer=UserResponse.model_validate(e.payer),
                splits=[
                    SplitResponse(**s.__dict__, user=UserResponse.model_validate(s.user))
                    for s in e.splits
                ]
            )
            for e in expenses
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get expense details."""
    result = await db.execute(
        select(Expense)
        .options(
            selectinload(Expense.payer),
            selectinload(Expense.splits).selectinload(ExpenseSplit.user),
            selectinload(Expense.comments),
            selectinload(Expense.reactions)
        )
        .where(and_(Expense.id == expense_id, Expense.is_deleted == False))
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    await check_group_membership(db, expense.group_id, current_user.id)

    return ExpenseResponse(
        **expense.__dict__,
        payer=UserResponse.model_validate(expense.payer),
        splits=[
            SplitResponse(**s.__dict__, user=UserResponse.model_validate(s.user))
            for s in expense.splits
        ],
        comment_count=len([c for c in expense.comments if not c.is_deleted]),
        reaction_count=len(expense.reactions)
    )


@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: uuid.UUID,
    data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an expense."""
    result = await db.execute(
        select(Expense)
        .options(selectinload(Expense.splits))
        .where(and_(Expense.id == expense_id, Expense.is_deleted == False))
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    await check_group_membership(db, expense.group_id, current_user.id)

    # Check if user can edit (creator or admin)
    membership = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == expense.group_id,
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
    )
    member = membership.scalar_one()

    if expense.created_by_id != current_user.id and member.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit your own expenses or be an admin"
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True, exclude={"splits", "participant_ids"})
    for field, value in update_data.items():
        setattr(expense, field, value)

    # Update splits if provided
    if data.splits is not None or data.participant_ids is not None:
        # Delete existing splits
        for split in expense.splits:
            await db.delete(split)

        amount = data.amount if data.amount else expense.amount
        split_type = data.split_type if data.split_type else expense.split_type

        if split_type == "equal" and data.participant_ids:
            splits_data = calculate_splits(amount, "equal", data.participant_ids, [])
        elif data.splits:
            splits_data = calculate_splits(
                amount,
                split_type,
                [s.user_id for s in data.splits],
                [s.model_dump() for s in data.splits]
            )
        else:
            splits_data = []

        for split_info in splits_data:
            split = ExpenseSplit(
                expense_id=expense.id,
                user_id=split_info["user_id"],
                amount=split_info["amount"],
                shares=split_info.get("shares"),
                percentage=split_info.get("percentage"),
            )
            db.add(split)

    await db.commit()

    # Reload
    result = await db.execute(
        select(Expense)
        .options(
            selectinload(Expense.payer),
            selectinload(Expense.splits).selectinload(ExpenseSplit.user)
        )
        .where(Expense.id == expense.id)
    )
    expense = result.scalar_one()

    return ExpenseResponse(
        **expense.__dict__,
        payer=UserResponse.model_validate(expense.payer),
        splits=[
            SplitResponse(**s.__dict__, user=UserResponse.model_validate(s.user))
            for s in expense.splits
        ]
    )


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an expense (soft delete)."""
    result = await db.execute(
        select(Expense).where(and_(Expense.id == expense_id, Expense.is_deleted == False))
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Check membership and permissions
    membership = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == expense.group_id,
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
    )
    member = membership.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    if expense.created_by_id != current_user.id and member.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own expenses or be an admin"
        )

    expense.is_deleted = True
    expense.deleted_at = datetime.utcnow()
    expense.deleted_by_id = current_user.id
    await db.commit()

    return {"message": "Expense deleted successfully"}


@router.post("/{expense_id}/receipt", response_model=ExpenseResponse)
async def upload_receipt(
    expense_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload receipt for an expense."""
    result = await db.execute(
        select(Expense)
        .options(
            selectinload(Expense.payer),
            selectinload(Expense.splits).selectinload(ExpenseSplit.user)
        )
        .where(and_(Expense.id == expense_id, Expense.is_deleted == False))
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    await check_group_membership(db, expense.group_id, current_user.id)

    # Validate file
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )

    upload_dir = os.path.join(settings.UPLOAD_DIR, "receipts")
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    expense.receipt_url = f"/uploads/receipts/{filename}"
    await db.commit()
    await db.refresh(expense)

    return ExpenseResponse(
        **expense.__dict__,
        payer=UserResponse.model_validate(expense.payer),
        splits=[
            SplitResponse(**s.__dict__, user=UserResponse.model_validate(s.user))
            for s in expense.splits
        ]
    )


# ==================== TEMPLATES ====================
@router.post("/templates", response_model=ExpenseTemplateResponse)
async def create_template(
    data: ExpenseTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create an expense template."""
    if data.group_id:
        await check_group_membership(db, data.group_id, current_user.id)

    template = ExpenseTemplate(
        user_id=current_user.id,
        group_id=data.group_id,
        name=data.name,
        amount=data.amount,
        category=data.category,
        split_type=data.split_type,
        split_data=data.split_data,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)

    return template


@router.get("/templates", response_model=List[ExpenseTemplateResponse])
async def list_templates(
    group_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List expense templates."""
    query = select(ExpenseTemplate).where(ExpenseTemplate.user_id == current_user.id)

    if group_id:
        query = query.where(
            or_(
                ExpenseTemplate.group_id == group_id,
                ExpenseTemplate.group_id == None
            )
        )

    result = await db.execute(query.order_by(ExpenseTemplate.created_at.desc()))
    templates = result.scalars().all()

    return templates


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an expense template."""
    result = await db.execute(
        select(ExpenseTemplate).where(
            and_(
                ExpenseTemplate.id == template_id,
                ExpenseTemplate.user_id == current_user.id
            )
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    await db.delete(template)
    await db.commit()

    return {"message": "Template deleted"}
