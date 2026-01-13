from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid as uuid_module

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models import User, Friendship, Group, Membership, Expense, ExpenseSplit, Payment
from app.schemas.friendship import (
    FriendRequestCreate, FriendshipResponse, FriendResponse, FriendListResponse
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.post("/request", response_model=FriendshipResponse, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    data: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a friend request by email."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    addressee = result.scalar_one_or_none()

    if not addressee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email"
        )

    if addressee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself"
        )

    # Check existing friendship (either direction)
    existing = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.requester_id == current_user.id, Friendship.addressee_id == addressee.id),
                and_(Friendship.requester_id == addressee.id, Friendship.addressee_id == current_user.id)
            )
        )
    )
    existing_friendship = existing.scalar_one_or_none()

    if existing_friendship:
        if existing_friendship.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends with this user"
            )
        elif existing_friendship.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A friend request already exists"
            )

    friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=addressee.id,
        status="pending"
    )
    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)

    return FriendshipResponse(
        id=friendship.id,
        requester_id=friendship.requester_id,
        addressee_id=friendship.addressee_id,
        status=friendship.status,
        friend_group_id=friendship.friend_group_id,
        created_at=friendship.created_at,
        accepted_at=friendship.accepted_at,
        friend=UserResponse.model_validate(addressee)
    )


@router.get("", response_model=FriendListResponse)
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all friends and pending requests."""
    # Get accepted friendships
    accepted = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.requester), selectinload(Friendship.addressee))
        .where(
            and_(
                or_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == current_user.id
                ),
                Friendship.status == "accepted"
            )
        )
    )
    accepted_friendships = accepted.scalars().all()

    friends = []
    for f in accepted_friendships:
        friend = f.addressee if f.requester_id == current_user.id else f.requester

        # Calculate balance from friend_group expenses
        balance = 0.0
        if f.friend_group_id:
            # What current user paid (expenses)
            paid_result = await db.execute(
                select(func.coalesce(func.sum(Expense.amount), 0)).where(
                    and_(
                        Expense.group_id == f.friend_group_id,
                        Expense.payer_id == current_user.id,
                        Expense.is_deleted == False
                    )
                )
            )
            paid = float(paid_result.scalar() or 0)

            # What current user owes (from splits)
            owed_result = await db.execute(
                select(func.coalesce(func.sum(ExpenseSplit.amount), 0))
                .select_from(ExpenseSplit)
                .join(Expense)
                .where(
                    and_(
                        Expense.group_id == f.friend_group_id,
                        ExpenseSplit.user_id == current_user.id,
                        Expense.is_deleted == False
                    )
                )
            )
            owed = float(owed_result.scalar() or 0)

            # Include confirmed payments - payments made by current user
            payments_made_result = await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    and_(
                        Payment.group_id == f.friend_group_id,
                        Payment.payer_id == current_user.id,
                        Payment.status == "confirmed"
                    )
                )
            )
            payments_made = float(payments_made_result.scalar() or 0)

            # Include confirmed payments - payments received by current user
            payments_received_result = await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    and_(
                        Payment.group_id == f.friend_group_id,
                        Payment.receiver_id == current_user.id,
                        Payment.status == "confirmed"
                    )
                )
            )
            payments_received = float(payments_received_result.scalar() or 0)

            # Balance = (what I paid + what I paid back) - (what I owe + what was paid to me)
            # Positive = friend owes me, Negative = I owe friend
            balance = (paid + payments_made) - (owed + payments_received)

        friends.append(FriendResponse(
            id=friend.id,
            email=friend.email,
            name=friend.name,
            profile_picture=friend.profile_picture,
            friendship_id=f.id,
            friend_group_id=f.friend_group_id,
            balance=balance
        ))

    # Get pending sent
    sent = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.addressee))
        .where(
            and_(
                Friendship.requester_id == current_user.id,
                Friendship.status == "pending"
            )
        )
    )
    pending_sent = [
        FriendshipResponse(
            id=f.id,
            requester_id=f.requester_id,
            addressee_id=f.addressee_id,
            status=f.status,
            friend_group_id=f.friend_group_id,
            created_at=f.created_at,
            accepted_at=f.accepted_at,
            friend=UserResponse.model_validate(f.addressee)
        )
        for f in sent.scalars().all()
    ]

    # Get pending received
    received = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.requester))
        .where(
            and_(
                Friendship.addressee_id == current_user.id,
                Friendship.status == "pending"
            )
        )
    )
    pending_received = [
        FriendshipResponse(
            id=f.id,
            requester_id=f.requester_id,
            addressee_id=f.addressee_id,
            status=f.status,
            friend_group_id=f.friend_group_id,
            created_at=f.created_at,
            accepted_at=f.accepted_at,
            friend=UserResponse.model_validate(f.requester)
        )
        for f in received.scalars().all()
    ]

    return FriendListResponse(
        friends=friends,
        pending_sent=pending_sent,
        pending_received=pending_received
    )


@router.post("/{friendship_id}/accept")
async def accept_friend_request(
    friendship_id: uuid_module.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a friend request."""
    result = await db.execute(
        select(Friendship)
        .options(selectinload(Friendship.requester))
        .where(
            and_(
                Friendship.id == friendship_id,
                Friendship.addressee_id == current_user.id,
                Friendship.status == "pending"
            )
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )

    # Create hidden friend group
    friend_group = Group(
        name=f"{current_user.name} & {friendship.requester.name}",
        description="Direct expenses between friends",
        category="friends",
        created_by_id=current_user.id,
        is_friend_group=True
    )
    db.add(friend_group)
    await db.flush()

    # Add both users as members
    for user_id in [current_user.id, friendship.requester_id]:
        membership = Membership(
            user_id=user_id,
            group_id=friend_group.id,
            role="admin"
        )
        db.add(membership)

    friendship.status = "accepted"
    friendship.accepted_at = datetime.utcnow()
    friendship.friend_group_id = friend_group.id

    await db.commit()

    return {"message": "Friend request accepted", "friend_group_id": str(friend_group.id)}


@router.post("/{friendship_id}/decline")
async def decline_friend_request(
    friendship_id: uuid_module.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Decline a friend request."""
    result = await db.execute(
        select(Friendship).where(
            and_(
                Friendship.id == friendship_id,
                Friendship.addressee_id == current_user.id,
                Friendship.status == "pending"
            )
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )

    friendship.status = "declined"
    await db.commit()

    return {"message": "Friend request declined"}


@router.delete("/{friendship_id}")
async def remove_friend(
    friendship_id: uuid_module.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a friend (unfriend). Only allowed if balance is settled."""
    result = await db.execute(
        select(Friendship).where(
            and_(
                Friendship.id == friendship_id,
                or_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == current_user.id
                ),
                Friendship.status == "accepted"
            )
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )

    # Check if balance is settled before allowing deletion
    if friendship.friend_group_id:
        # Calculate balance from expenses
        paid_result = await db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                and_(
                    Expense.group_id == friendship.friend_group_id,
                    Expense.payer_id == current_user.id,
                    Expense.is_deleted == False
                )
            )
        )
        paid = float(paid_result.scalar() or 0)

        owed_result = await db.execute(
            select(func.coalesce(func.sum(ExpenseSplit.amount), 0))
            .select_from(ExpenseSplit)
            .join(Expense)
            .where(
                and_(
                    Expense.group_id == friendship.friend_group_id,
                    ExpenseSplit.user_id == current_user.id,
                    Expense.is_deleted == False
                )
            )
        )
        owed = float(owed_result.scalar() or 0)

        # Include confirmed payments
        payments_made_result = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                and_(
                    Payment.group_id == friendship.friend_group_id,
                    Payment.payer_id == current_user.id,
                    Payment.status == "confirmed"
                )
            )
        )
        payments_made = float(payments_made_result.scalar() or 0)

        payments_received_result = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                and_(
                    Payment.group_id == friendship.friend_group_id,
                    Payment.receiver_id == current_user.id,
                    Payment.status == "confirmed"
                )
            )
        )
        payments_received = float(payments_received_result.scalar() or 0)

        balance = (paid + payments_made) - (owed + payments_received)

        # If balance is not zero (within a small tolerance), prevent deletion
        if abs(balance) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot remove friend with unsettled balance. Please settle up first. Balance: {balance:.2f}"
            )

    # Keep the friend group for expense history, just delete the friendship
    await db.delete(friendship)
    await db.commit()

    return {"message": "Friend removed"}


@router.get("/{friend_id}/group")
async def get_friend_group(
    friend_id: uuid_module.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the friend group ID for adding expenses with a friend."""
    # Find friendship
    result = await db.execute(
        select(Friendship).where(
            and_(
                or_(
                    and_(Friendship.requester_id == current_user.id, Friendship.addressee_id == friend_id),
                    and_(Friendship.requester_id == friend_id, Friendship.addressee_id == current_user.id)
                ),
                Friendship.status == "accepted"
            )
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship or not friendship.friend_group_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found or no group exists"
        )

    return {"group_id": str(friendship.friend_group_id)}
