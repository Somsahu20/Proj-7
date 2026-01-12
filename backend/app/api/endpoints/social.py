from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models import User, Expense, Comment, Reaction, ActivityLog, Membership
from app.schemas import (
    CommentCreate, CommentUpdate, CommentResponse,
    ReactionCreate, ReactionResponse, ReactionSummary,
    ActivityResponse, ActivityListResponse, UserResponse
)

router = APIRouter(tags=["Social"])


# ==================== COMMENTS ====================
comments_router = APIRouter(prefix="/expenses/{expense_id}/comments", tags=["Comments"])


async def check_expense_access(db: AsyncSession, expense_id: uuid.UUID, user_id: uuid.UUID) -> Expense:
    """Check if user has access to the expense."""
    result = await db.execute(
        select(Expense).where(
            and_(Expense.id == expense_id, Expense.is_deleted == False)
        )
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Check membership
    membership = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == expense.group_id,
                Membership.user_id == user_id,
                Membership.is_active == True
            )
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    return expense


@comments_router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    expense_id: uuid.UUID,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a comment to an expense."""
    expense = await check_expense_access(db, expense_id, current_user.id)

    # Check parent comment if replying
    if data.parent_id:
        parent_result = await db.execute(
            select(Comment).where(
                and_(
                    Comment.id == data.parent_id,
                    Comment.expense_id == expense_id,
                    Comment.is_deleted == False
                )
            )
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )

    comment = Comment(
        expense_id=expense_id,
        user_id=current_user.id,
        parent_id=data.parent_id,
        content=data.content,
        mentions=[str(m) for m in data.mentions],
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return CommentResponse(
        **comment.__dict__,
        user=UserResponse.model_validate(current_user),
        mentions=[uuid.UUID(m) for m in comment.mentions] if comment.mentions else []
    )


@comments_router.get("", response_model=List[CommentResponse])
async def list_comments(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List comments for an expense."""
    await check_expense_access(db, expense_id, current_user.id)

    # Get top-level comments with replies
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user), selectinload(Comment.replies).selectinload(Comment.user))
        .where(
            and_(
                Comment.expense_id == expense_id,
                Comment.parent_id == None,
                Comment.is_deleted == False
            )
        )
        .order_by(Comment.created_at)
    )
    comments = result.scalars().all()

    def build_comment_response(comment: Comment) -> CommentResponse:
        return CommentResponse(
            id=comment.id,
            expense_id=comment.expense_id,
            user_id=comment.user_id,
            parent_id=comment.parent_id,
            content=comment.content,
            mentions=[uuid.UUID(m) for m in comment.mentions] if comment.mentions else [],
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user=UserResponse.model_validate(comment.user),
            replies=[build_comment_response(r) for r in comment.replies if not r.is_deleted]
        )

    return [build_comment_response(c) for c in comments]


@comments_router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    expense_id: uuid.UUID,
    comment_id: uuid.UUID,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a comment."""
    await check_expense_access(db, expense_id, current_user.id)

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(
            and_(
                Comment.id == comment_id,
                Comment.expense_id == expense_id,
                Comment.is_deleted == False
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit your own comments"
        )

    comment.content = data.content
    comment.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(comment)

    return CommentResponse(
        **comment.__dict__,
        user=UserResponse.model_validate(comment.user),
        mentions=[uuid.UUID(m) for m in comment.mentions] if comment.mentions else []
    )


@comments_router.delete("/{comment_id}")
async def delete_comment(
    expense_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a comment (soft delete)."""
    await check_expense_access(db, expense_id, current_user.id)

    result = await db.execute(
        select(Comment).where(
            and_(
                Comment.id == comment_id,
                Comment.expense_id == expense_id,
                Comment.is_deleted == False
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own comments"
        )

    comment.is_deleted = True
    comment.deleted_at = datetime.utcnow()
    await db.commit()

    return {"message": "Comment deleted"}


# ==================== REACTIONS ====================
reactions_router = APIRouter(prefix="/expenses/{expense_id}/reactions", tags=["Reactions"])


@reactions_router.post("", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
async def add_reaction(
    expense_id: uuid.UUID,
    data: ReactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a reaction to an expense."""
    await check_expense_access(db, expense_id, current_user.id)

    # Check if reaction already exists
    existing = await db.execute(
        select(Reaction).where(
            and_(
                Reaction.expense_id == expense_id,
                Reaction.user_id == current_user.id,
                Reaction.emoji == data.emoji
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already reacted with this emoji"
        )

    reaction = Reaction(
        expense_id=expense_id,
        user_id=current_user.id,
        emoji=data.emoji,
    )
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)

    return ReactionResponse(
        **reaction.__dict__,
        user=UserResponse.model_validate(current_user)
    )


@reactions_router.get("", response_model=List[ReactionSummary])
async def list_reactions(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List reactions for an expense (grouped by emoji)."""
    await check_expense_access(db, expense_id, current_user.id)

    result = await db.execute(
        select(Reaction)
        .options(selectinload(Reaction.user))
        .where(Reaction.expense_id == expense_id)
    )
    reactions = result.scalars().all()

    # Group by emoji
    emoji_groups = {}
    for reaction in reactions:
        if reaction.emoji not in emoji_groups:
            emoji_groups[reaction.emoji] = []
        emoji_groups[reaction.emoji].append(UserResponse.model_validate(reaction.user))

    return [
        ReactionSummary(
            emoji=emoji,
            count=len(users),
            users=users
        )
        for emoji, users in emoji_groups.items()
    ]


@reactions_router.delete("/{emoji}")
async def remove_reaction(
    expense_id: uuid.UUID,
    emoji: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a reaction from an expense."""
    await check_expense_access(db, expense_id, current_user.id)

    result = await db.execute(
        select(Reaction).where(
            and_(
                Reaction.expense_id == expense_id,
                Reaction.user_id == current_user.id,
                Reaction.emoji == emoji
            )
        )
    )
    reaction = result.scalar_one_or_none()

    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )

    await db.delete(reaction)
    await db.commit()

    return {"message": "Reaction removed"}


# ==================== ACTIVITY LOG ====================
activity_router = APIRouter(prefix="/groups/{group_id}/activity", tags=["Activity"])


@activity_router.get("", response_model=ActivityListResponse)
async def list_group_activity(
    group_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List activity for a group."""
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

    # Count
    count_result = await db.execute(
        select(func.count()).where(ActivityLog.group_id == group_id)
    )
    total = count_result.scalar()

    # Get paginated
    result = await db.execute(
        select(ActivityLog)
        .options(selectinload(ActivityLog.user))
        .where(ActivityLog.group_id == group_id)
        .order_by(ActivityLog.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    activities = result.scalars().all()

    return ActivityListResponse(
        activities=[
            ActivityResponse(
                **a.__dict__,
                user=UserResponse.model_validate(a.user) if a.user else None
            )
            for a in activities
        ],
        total=total,
        page=page,
        per_page=per_page
    )


# Include routers
router.include_router(comments_router)
router.include_router(reactions_router)
router.include_router(activity_router)
