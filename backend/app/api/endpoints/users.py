from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import List
import os
import uuid
import aiofiles

from app.db.database import get_db
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import User, Invitation, Membership
from app.schemas import (
    UserResponse, UserProfileResponse, UserUpdate,
    PasswordChange, NotificationPreferencesUpdate
)
from app.schemas.group import InvitationResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload user avatar."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, WebP"
        )

    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    # Generate filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    # Save file
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    # Update user
    current_user.profile_picture = f"/uploads/avatars/{filename}"
    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/me/change-password")
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user's password."""
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth-only accounts"
        )

    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.patch("/me/notification-preferences", response_model=UserProfileResponse)
async def update_notification_preferences(
    data: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update notification preferences."""
    current_user.notification_preferences = data.model_dump()
    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.delete("/me")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate current user's account."""
    current_user.is_active = False
    await db.commit()

    return {"message": "Account deactivated successfully"}


# ==================== INVITATION ENDPOINTS ====================

@router.get("/me/invitations", response_model=List[InvitationResponse])
async def get_my_invitations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pending invitations for current user."""
    result = await db.execute(
        select(Invitation)
        .options(
            selectinload(Invitation.group),
            selectinload(Invitation.invited_by)
        )
        .where(
            and_(
                Invitation.email == current_user.email,
                Invitation.status == "pending",
                Invitation.expires_at > datetime.now(timezone.utc)
            )
        )
        .order_by(Invitation.created_at.desc())
    )
    invitations = result.scalars().all()

    return [
        InvitationResponse(
            id=i.id,
            group_id=i.group_id,
            email=i.email,
            status=i.status,
            expires_at=i.expires_at,
            created_at=i.created_at,
            group_name=i.group.name if i.group else None,
            invited_by_name=i.invited_by.name if i.invited_by else None
        )
        for i in invitations
    ]


@router.post("/me/invitations/{invitation_id}/accept")
async def accept_invitation_by_id(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a group invitation by ID."""
    result = await db.execute(
        select(Invitation).where(
            and_(
                Invitation.id == invitation_id,
                Invitation.email == current_user.email,
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

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )

    # Check existing membership
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


@router.post("/me/invitations/{invitation_id}/decline")
async def decline_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Decline a group invitation."""
    result = await db.execute(
        select(Invitation).where(
            and_(
                Invitation.id == invitation_id,
                Invitation.email == current_user.email,
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

    invitation.status = "declined"
    invitation.declined_at = datetime.utcnow()
    await db.commit()

    return {"message": "Invitation declined"}
