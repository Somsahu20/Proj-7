from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import os
import uuid
import aiofiles

from app.db.database import get_db
from app.api.deps import get_current_user
from app.core.config import settings
from app.models import User, Group, Membership, Payment, PaymentProof
from app.schemas import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse,
    PaymentProofResponse, PaymentReject, PaymentCancel, UserResponse
)

router = APIRouter(prefix="/payments", tags=["Payments"])


async def check_group_membership(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID):
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
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a new payment (payer records it)."""
    await check_group_membership(db, data.group_id, current_user.id)

    # Check receiver is also a member
    await check_group_membership(db, data.group_id, data.receiver_id)

    if current_user.id == data.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pay yourself"
        )

    payment = Payment(
        group_id=data.group_id,
        payer_id=current_user.id,
        receiver_id=data.receiver_id,
        amount=data.amount,
        description=data.description,
        payment_method=data.payment_method,
        date=data.date,
        status="pending",
    )
    db.add(payment)
    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.payer),
            selectinload(Payment.receiver),
            selectinload(Payment.proofs)
        )
        .where(Payment.id == payment.id)
    )
    payment = result.scalar_one()

    return PaymentResponse(
        **payment.__dict__,
        payer=UserResponse.model_validate(payment.payer),
        receiver=UserResponse.model_validate(payment.receiver),
        proofs=[PaymentProofResponse(**p.__dict__) for p in payment.proofs]
    )


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    group_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List payments (optionally filtered by group)."""
    query = select(Payment).where(
        and_(
            Payment.payer_id == current_user.id
        ) | and_(
            Payment.receiver_id == current_user.id
        )
    )

    if group_id:
        await check_group_membership(db, group_id, current_user.id)
        query = query.where(Payment.group_id == group_id)

    if status_filter:
        query = query.where(Payment.status == status_filter)

    # Count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    # Get paginated
    query = query.options(
        selectinload(Payment.payer),
        selectinload(Payment.receiver),
        selectinload(Payment.proofs)
    ).order_by(Payment.created_at.desc())

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    payments = result.scalars().all()

    return PaymentListResponse(
        payments=[
            PaymentResponse(
                **p.__dict__,
                payer=UserResponse.model_validate(p.payer),
                receiver=UserResponse.model_validate(p.receiver),
                proofs=[PaymentProofResponse(**pr.__dict__) for pr in p.proofs]
            )
            for p in payments
        ],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/pending", response_model=List[PaymentResponse])
async def list_pending_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List payments pending your confirmation (as receiver)."""
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.payer),
            selectinload(Payment.receiver),
            selectinload(Payment.proofs)
        )
        .where(
            and_(
                Payment.receiver_id == current_user.id,
                Payment.status == "pending"
            )
        )
        .order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()

    return [
        PaymentResponse(
            **p.__dict__,
            payer=UserResponse.model_validate(p.payer),
            receiver=UserResponse.model_validate(p.receiver),
            proofs=[PaymentProofResponse(**pr.__dict__) for pr in p.proofs]
        )
        for p in payments
    ]


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment details."""
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.payer),
            selectinload(Payment.receiver),
            selectinload(Payment.proofs)
        )
        .where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Check access
    if payment.payer_id != current_user.id and payment.receiver_id != current_user.id:
        await check_group_membership(db, payment.group_id, current_user.id)

    return PaymentResponse(
        **payment.__dict__,
        payer=UserResponse.model_validate(payment.payer),
        receiver=UserResponse.model_validate(payment.receiver),
        proofs=[PaymentProofResponse(**p.__dict__) for p in payment.proofs]
    )


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm a payment (receiver only)."""
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.payer),
            selectinload(Payment.receiver),
            selectinload(Payment.proofs)
        )
        .where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the receiver can confirm this payment"
        )

    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment cannot be confirmed (current status: {payment.status})"
        )

    payment.status = "confirmed"
    payment.confirmed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(payment)

    return PaymentResponse(
        **payment.__dict__,
        payer=UserResponse.model_validate(payment.payer),
        receiver=UserResponse.model_validate(payment.receiver),
        proofs=[PaymentProofResponse(**p.__dict__) for p in payment.proofs]
    )


@router.post("/{payment_id}/reject", response_model=PaymentResponse)
async def reject_payment(
    payment_id: uuid.UUID,
    data: PaymentReject,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a payment (receiver only)."""
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.payer),
            selectinload(Payment.receiver),
            selectinload(Payment.proofs)
        )
        .where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the receiver can reject this payment"
        )

    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment cannot be rejected (current status: {payment.status})"
        )

    payment.status = "rejected"
    payment.rejected_at = datetime.utcnow()
    payment.rejected_reason = data.reason
    await db.commit()
    await db.refresh(payment)

    return PaymentResponse(
        **payment.__dict__,
        payer=UserResponse.model_validate(payment.payer),
        receiver=UserResponse.model_validate(payment.receiver),
        proofs=[PaymentProofResponse(**p.__dict__) for p in payment.proofs]
    )


@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
async def cancel_payment(
    payment_id: uuid.UUID,
    data: PaymentCancel,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a payment (payer only, if still pending)."""
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.payer),
            selectinload(Payment.receiver),
            selectinload(Payment.proofs)
        )
        .where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.payer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the payer can cancel this payment"
        )

    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment cannot be cancelled (current status: {payment.status})"
        )

    payment.status = "cancelled"
    payment.cancelled_at = datetime.utcnow()
    payment.cancelled_reason = data.reason
    await db.commit()
    await db.refresh(payment)

    return PaymentResponse(
        **payment.__dict__,
        payer=UserResponse.model_validate(payment.payer),
        receiver=UserResponse.model_validate(payment.receiver),
        proofs=[PaymentProofResponse(**p.__dict__) for p in payment.proofs]
    )


@router.post("/{payment_id}/proof", response_model=PaymentProofResponse)
async def upload_payment_proof(
    payment_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload payment proof (payer only)."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.payer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the payer can upload proof"
        )

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

    upload_dir = os.path.join(settings.UPLOAD_DIR, "payment_proofs")
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    proof = PaymentProof(
        payment_id=payment_id,
        file_url=f"/uploads/payment_proofs/{filename}",
        file_type=file.content_type,
        file_size=len(contents),
    )
    db.add(proof)
    await db.commit()
    await db.refresh(proof)

    return proof
