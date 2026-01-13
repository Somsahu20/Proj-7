from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import os
import uuid
import secrets
import aiofiles

from app.db.database import get_db
from app.api.deps import get_current_user
from app.core.config import settings
from app.models import User, Group, Membership, Invitation, Expense, ExpenseSplit
from app.schemas import (
    GroupCreate, GroupUpdate, GroupResponse, GroupDetailResponse,
    MemberResponse, MemberRoleUpdate,
    InvitationCreate, InvitationResponse, InvitationAccept, UserResponse
)

router = APIRouter(prefix="/groups", tags=["Groups"])


def build_group_response(group, member_count: int = 0) -> GroupResponse:
    """Build GroupResponse with explicit fields."""
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        category=group.category,
        image_url=group.image_url,
        created_by_id=group.created_by_id,
        is_archived=group.is_archived,
        settings=group.settings or {},
        created_at=group.created_at,
        member_count=member_count
    )


def build_member_response(m) -> MemberResponse:
    """Build MemberResponse with explicit fields."""
    return MemberResponse(
        id=m.id,
        user_id=m.user_id,
        group_id=m.group_id,
        role=m.role,
        joined_at=m.joined_at,
        is_active=m.is_active,
        user=UserResponse.model_validate(m.user) if m.user else None
    )


def build_invitation_response(invitation, group_name: str = None, invited_by_name: str = None) -> InvitationResponse:
    """Build InvitationResponse with explicit fields."""
    return InvitationResponse(
        id=invitation.id,
        group_id=invitation.group_id,
        email=invitation.email,
        status=invitation.status,
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
        group_name=group_name,
        invited_by_name=invited_by_name
    )


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new group."""
    group = Group(
        name=data.name,
        description=data.description,
        category=data.category,
        created_by_id=current_user.id,
    )
    db.add(group)
    await db.flush()

    # Add creator as admin
    membership = Membership(
        user_id=current_user.id,
        group_id=group.id,
        role="admin",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(group)

    return build_group_response(group, member_count=1)


@router.get("", response_model=List[GroupResponse])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all groups for current user."""
    # First, get the groups the user is a member of
    user_groups_subq = (
        select(Membership.group_id)
        .where(
            and_(
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
        .scalar_subquery()
    )

    # Then count all active members for each of those groups
    result = await db.execute(
        select(Group, func.count(Membership.id).label("member_count"))
        .join(Membership, Membership.group_id == Group.id)
        .where(
            and_(
                Group.id.in_(user_groups_subq),
                Membership.is_active == True,
                Group.is_deleted == False
            )
        )
        .group_by(Group.id)
        .order_by(Group.created_at.desc())
    )
    groups = result.all()

    return [build_group_response(group, member_count=count) for group, count in groups]


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get group details."""
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

    # Get group with creator
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.creator))
        .where(and_(Group.id == group_id, Group.is_deleted == False))
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Get members
    members_result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.user))
        .where(
            and_(
                Membership.group_id == group_id,
                Membership.is_active == True
            )
        )
    )
    members = members_result.scalars().all()

    # Calculate total expenses
    expenses_result = await db.execute(
        select(func.sum(Expense.amount))
        .where(
            and_(
                Expense.group_id == group_id,
                Expense.is_deleted == False
            )
        )
    )
    total_expenses = expenses_result.scalar() or 0

    # Calculate user's balance in this group
    # Money paid by user
    paid_result = await db.execute(
        select(func.sum(Expense.amount))
        .where(
            and_(
                Expense.group_id == group_id,
                Expense.payer_id == current_user.id,
                Expense.is_deleted == False
            )
        )
    )
    paid = paid_result.scalar() or 0

    # Money owed by user (from splits)
    owed_result = await db.execute(
        select(func.sum(ExpenseSplit.amount))
        .join(Expense, Expense.id == ExpenseSplit.expense_id)
        .where(
            and_(
                Expense.group_id == group_id,
                ExpenseSplit.user_id == current_user.id,
                Expense.is_deleted == False
            )
        )
    )
    owed = owed_result.scalar() or 0

    your_balance = float(paid) - float(owed)

    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        category=group.category,
        image_url=group.image_url,
        created_by_id=group.created_by_id,
        is_archived=group.is_archived,
        settings=group.settings,
        created_at=group.created_at,
        member_count=len(members),
        creator=UserResponse.model_validate(group.creator),
        members=[MemberResponse(
            id=m.id,
            user_id=m.user_id,
            group_id=m.group_id,
            role=m.role,
            joined_at=m.joined_at,
            is_active=m.is_active,
            user=UserResponse.model_validate(m.user)
        ) for m in members],
        total_expenses=float(total_expenses),
        your_balance=your_balance
    )


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: uuid.UUID,
    data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update group settings (admin only)."""
    # Check admin
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
            detail="Admin access required"
        )

    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)

    return group


@router.delete("/{group_id}")
async def delete_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete group (admin only, soft delete)."""
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
            detail="Admin access required"
        )

    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    group.is_deleted = True
    group.deleted_at = datetime.utcnow()
    await db.commit()

    return {"message": "Group deleted successfully"}


@router.post("/{group_id}/image", response_model=GroupResponse)
async def upload_group_image(
    group_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload group image (admin only)."""
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
            detail="Admin access required"
        )

    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Validate and save file
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
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

    upload_dir = os.path.join(settings.UPLOAD_DIR, "groups")
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    group.image_url = f"/uploads/groups/{filename}"
    await db.commit()
    await db.refresh(group)

    return group


# ==================== MEMBERS ====================
@router.get("/{group_id}/members", response_model=List[MemberResponse])
async def list_members(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List group members."""
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

    result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.user))
        .where(
            and_(
                Membership.group_id == group_id,
                Membership.is_active == True
            )
        )
    )
    members = result.scalars().all()

    return [build_member_response(m) for m in members]


@router.patch("/{group_id}/members/{user_id}/role", response_model=MemberResponse)
async def update_member_role(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    data: MemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update member role (admin only)."""
    # Check admin
    admin_check = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == current_user.id,
                Membership.role == "admin",
                Membership.is_active == True
            )
        )
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Get target membership
    result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.user))
        .where(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    membership.role = data.role
    await db.commit()
    await db.refresh(membership)

    return build_member_response(membership)


@router.delete("/{group_id}/members/{user_id}")
async def remove_member(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove member from group (admin only, or self-leave)."""
    is_self = user_id == current_user.id

    if not is_self:
        # Check admin
        admin_check = await db.execute(
            select(Membership).where(
                and_(
                    Membership.group_id == group_id,
                    Membership.user_id == current_user.id,
                    Membership.role == "admin",
                    Membership.is_active == True
                )
            )
        )
        if not admin_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    membership.is_active = False
    membership.left_at = datetime.utcnow()
    await db.commit()

    return {"message": "Member removed successfully"}


# ==================== INVITATIONS ====================
@router.post("/{group_id}/invitations", response_model=InvitationResponse)
async def create_invitation(
    group_id: uuid.UUID,
    data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create group invitation."""
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

    # Check if already a member
    existing = await db.execute(
        select(Membership)
        .join(User, User.id == Membership.user_id)
        .where(
            and_(
                Membership.group_id == group_id,
                User.email == data.email,
                Membership.is_active == True
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )

    # Check existing pending invitation
    pending = await db.execute(
        select(Invitation).where(
            and_(
                Invitation.group_id == group_id,
                Invitation.email == data.email,
                Invitation.status == "pending"
            )
        )
    )
    if pending.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already sent"
        )

    # Get group name
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one()

    invitation = Invitation(
        group_id=group_id,
        email=data.email,
        invited_by_id=current_user.id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    # TODO: Send invitation email

    return build_invitation_response(invitation, group_name=group.name, invited_by_name=current_user.name)


@router.get("/{group_id}/invitations", response_model=List[InvitationResponse])
async def list_invitations(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List pending invitations for a group."""
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

    result = await db.execute(
        select(Invitation).where(
            and_(
                Invitation.group_id == group_id,
                Invitation.status == "pending"
            )
        )
    )
    invitations = result.scalars().all()

    return [build_invitation_response(i) for i in invitations]


@router.post("/invitations/accept")
async def accept_invitation(
    data: InvitationAccept,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a group invitation."""
    result = await db.execute(
        select(Invitation).where(
            and_(
                Invitation.token == data.token,
                Invitation.status == "pending"
            )
        )
    )
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invitation"
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )

    # Check if already a member
    existing = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == invitation.group_id,
                Membership.user_id == current_user.id
            )
        )
    )
    member = existing.scalar_one_or_none()

    if member:
        if member.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already a member of this group"
            )
        else:
            member.is_active = True
            member.left_at = None
            member.joined_at = datetime.utcnow()
    else:
        membership = Membership(
            user_id=current_user.id,
            group_id=invitation.group_id,
            role="member",
            invited_by_id=invitation.invited_by_id,
        )
        db.add(membership)

    invitation.status = "accepted"
    invitation.accepted_at = datetime.utcnow()
    await db.commit()

    return {"message": "Invitation accepted", "group_id": str(invitation.group_id)}


@router.delete("/{group_id}/invitations/{invitation_id}")
async def cancel_invitation(
    group_id: uuid.UUID,
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending invitation."""
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

    result = await db.execute(
        select(Invitation).where(
            and_(
                Invitation.id == invitation_id,
                Invitation.group_id == group_id,
                Invitation.status == "pending"
            )
        )
    )
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    await db.delete(invitation)
    await db.commit()

    return {"message": "Invitation cancelled"}
