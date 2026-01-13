from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models import User, Expense, Payment, Dispute, DisputeVote, Membership
from app.schemas import (
    DisputeCreate, DisputeResponse, DisputeVoteCreate,
    DisputeVoteResponse, DisputeResolve
)

router = APIRouter(prefix="/disputes", tags=["Disputes"])


def build_vote_response(v) -> DisputeVoteResponse:
    """Build DisputeVoteResponse with explicit fields."""
    return DisputeVoteResponse(
        id=v.id,
        dispute_id=v.dispute_id,
        user_id=v.user_id,
        vote=v.vote,
        comment=v.comment,
        created_at=v.created_at
    )


def build_dispute_response(dispute, votes=None) -> DisputeResponse:
    """Build DisputeResponse with explicit fields."""
    vote_list = votes if votes is not None else (dispute.votes if hasattr(dispute, 'votes') and dispute.votes else [])
    return DisputeResponse(
        id=dispute.id,
        expense_id=dispute.expense_id,
        payment_id=dispute.payment_id,
        opened_by_id=dispute.opened_by_id,
        reason=dispute.reason,
        description=dispute.description,
        evidence_urls=dispute.evidence_urls or [],
        status=dispute.status,
        resolution=dispute.resolution,
        resolved_by_id=dispute.resolved_by_id,
        resolved_at=dispute.resolved_at,
        resolution_notes=dispute.resolution_notes,
        voting_ends_at=dispute.voting_ends_at if hasattr(dispute, 'voting_ends_at') else None,
        created_at=dispute.created_at,
        votes=[build_vote_response(v) for v in vote_list],
        vote_summary={
            "approve": len([v for v in vote_list if v.vote == "approve"]),
            "reject": len([v for v in vote_list if v.vote == "reject"]),
            "abstain": len([v for v in vote_list if v.vote == "abstain"]),
        } if vote_list else None
    )


@router.post("", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def create_dispute(
    data: DisputeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Open a dispute on an expense or payment."""
    if not data.expense_id and not data.payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify either expense_id or payment_id"
        )

    group_id = None

    # Verify expense/payment exists and user has access
    if data.expense_id:
        result = await db.execute(
            select(Expense).where(
                and_(Expense.id == data.expense_id, Expense.is_deleted == False)
            )
        )
        expense = result.scalar_one_or_none()
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        group_id = expense.group_id

    if data.payment_id:
        result = await db.execute(
            select(Payment).where(Payment.id == data.payment_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        group_id = payment.group_id

    # Check membership
    membership = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    dispute = Dispute(
        expense_id=data.expense_id,
        payment_id=data.payment_id,
        opened_by_id=current_user.id,
        reason=data.reason,
        description=data.description,
        evidence_urls=data.evidence_urls,
        status="open",
    )
    db.add(dispute)
    await db.commit()
    await db.refresh(dispute)

    return build_dispute_response(dispute, votes=[])


@router.get("", response_model=List[DisputeResponse])
async def list_disputes(
    expense_id: Optional[uuid.UUID] = None,
    payment_id: Optional[uuid.UUID] = None,
    group_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List disputes the user has access to."""
    # Get user's groups
    memberships_result = await db.execute(
        select(Membership.group_id).where(
            and_(
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
    )
    group_ids = [row[0] for row in memberships_result.all()]

    if group_id and group_id not in group_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    # Build query
    query = select(Dispute).options(selectinload(Dispute.votes))

    if expense_id:
        query = query.where(Dispute.expense_id == expense_id)
    elif payment_id:
        query = query.where(Dispute.payment_id == payment_id)
    else:
        # Filter by accessible groups (optionally scoped to a single group)
        if group_id:
            expense_subq = select(Expense.id).where(Expense.group_id == group_id)
            payment_subq = select(Payment.id).where(Payment.group_id == group_id)
        else:
            expense_subq = select(Expense.id).where(Expense.group_id.in_(group_ids))
            payment_subq = select(Payment.id).where(Payment.group_id.in_(group_ids))
        query = query.where(
            (Dispute.expense_id.in_(expense_subq)) | (Dispute.payment_id.in_(payment_subq))
        )

    if status_filter:
        query = query.where(Dispute.status == status_filter)

    query = query.order_by(Dispute.created_at.desc())
    result = await db.execute(query)
    disputes = result.scalars().all()

    return [build_dispute_response(d) for d in disputes]


@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(
    dispute_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dispute details."""
    result = await db.execute(
        select(Dispute)
        .options(selectinload(Dispute.votes))
        .where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )

    return build_dispute_response(dispute)


@router.post("/{dispute_id}/vote", response_model=DisputeVoteResponse)
async def vote_on_dispute(
    dispute_id: uuid.UUID,
    data: DisputeVoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Vote on a dispute."""
    result = await db.execute(
        select(Dispute).where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )

    if dispute.status not in ["open", "voting"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute is not open for voting"
        )

    # Check if already voted
    existing = await db.execute(
        select(DisputeVote).where(
            and_(
                DisputeVote.dispute_id == dispute_id,
                DisputeVote.user_id == current_user.id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted"
        )

    vote = DisputeVote(
        dispute_id=dispute_id,
        user_id=current_user.id,
        vote=data.vote,
        comment=data.comment,
    )
    db.add(vote)

    # Update dispute status if first vote
    if dispute.status == "open":
        dispute.status = "voting"

    await db.commit()
    await db.refresh(vote)

    return vote


@router.post("/{dispute_id}/resolve", response_model=DisputeResponse)
async def resolve_dispute(
    dispute_id: uuid.UUID,
    data: DisputeResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resolve a dispute (admin only)."""
    result = await db.execute(
        select(Dispute)
        .options(selectinload(Dispute.votes))
        .where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )

    if dispute.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute is already resolved"
        )

    # Check if user is admin of the group
    group_id = None
    if dispute.expense_id:
        expense_result = await db.execute(
            select(Expense.group_id).where(Expense.id == dispute.expense_id)
        )
        group_id = expense_result.scalar_one()
    elif dispute.payment_id:
        payment_result = await db.execute(
            select(Payment.group_id).where(Payment.id == dispute.payment_id)
        )
        group_id = payment_result.scalar_one()

    membership = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == current_user.id,
                Membership.role == "admin",
                Membership.is_active == True
            )
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to resolve disputes"
        )

    dispute.status = "resolved"
    dispute.resolution = data.resolution
    dispute.resolved_by_id = current_user.id
    dispute.resolved_at = datetime.utcnow()
    dispute.resolution_notes = data.resolution_notes

    if dispute.payment_id:
        payment_result = await db.execute(
            select(Payment).where(Payment.id == dispute.payment_id)
        )
        payment = payment_result.scalar_one_or_none()
        if payment:
            if data.resolution == "upheld":
                payment.status = "rejected"
                payment.rejected_at = datetime.utcnow()
                payment.rejected_reason = "Dispute upheld"
                payment.confirmed_at = None
            else:
                payment.status = "confirmed"
                payment.confirmed_at = datetime.utcnow()
                payment.rejected_at = None
                payment.rejected_reason = None

    await db.commit()
    await db.refresh(dispute)

    return build_dispute_response(dispute)
