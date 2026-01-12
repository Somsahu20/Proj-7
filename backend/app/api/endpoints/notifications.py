from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, AsyncGenerator
from datetime import datetime
import uuid
import asyncio
import json

from sse_starlette.sse import EventSourceResponse

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models import User, Notification, Membership
from app.schemas import (
    NotificationResponse, NotificationListResponse, UnreadCountResponse,
    MarkReadRequest
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Store for SSE connections (in production, use Redis)
sse_connections: dict = {}


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    type_filter: Optional[str] = Query(None, alias="type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's notifications."""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    if type_filter:
        query = query.where(Notification.type == type_filter)

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    # Count unread
    unread_result = await db.execute(
        select(func.count()).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
    )
    unread_count = unread_result.scalar()

    # Get paginated
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    notifications = result.scalars().all()

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        unread_count=unread_count,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get unread notification count."""
    # Total unread
    total_result = await db.execute(
        select(func.count()).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
    )
    total = total_result.scalar()

    # By type
    by_type_result = await db.execute(
        select(Notification.type, func.count())
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
        .group_by(Notification.type)
    )
    by_type = {t: c for t, c in by_type_result.all()}

    return UnreadCountResponse(
        unread_count=total,
        by_type=by_type
    )


@router.post("/mark-read")
async def mark_notifications_read(
    data: MarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark specific notifications as read."""
    await db.execute(
        update(Notification)
        .where(
            and_(
                Notification.id.in_(data.notification_ids),
                Notification.user_id == current_user.id
            )
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    await db.commit()

    return {"message": f"Marked {len(data.notification_ids)} notifications as read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read."""
    result = await db.execute(
        update(Notification)
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    await db.commit()

    return {"message": "All notifications marked as read"}


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific notification."""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification."""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    await db.delete(notification)
    await db.commit()

    return {"message": "Notification deleted"}


# ==================== SSE ENDPOINTS ====================
async def event_generator(user_id: uuid.UUID) -> AsyncGenerator:
    """Generate SSE events for a user."""
    queue = asyncio.Queue()
    sse_connections[str(user_id)] = queue

    try:
        while True:
            # Wait for events
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {
                    "event": event.get("event", "message"),
                    "id": event.get("id"),
                    "data": json.dumps(event.get("data", {}))
                }
            except asyncio.TimeoutError:
                # Send keepalive
                yield {"event": "ping", "data": ""}
    finally:
        sse_connections.pop(str(user_id), None)


@router.get("/stream/events")
async def sse_events(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """SSE endpoint for real-time notifications."""
    return EventSourceResponse(event_generator(current_user.id))


async def send_sse_event(user_id: uuid.UUID, event_type: str, data: dict):
    """Send an SSE event to a specific user."""
    queue = sse_connections.get(str(user_id))
    if queue:
        await queue.put({
            "event": event_type,
            "id": str(uuid.uuid4()),
            "data": data
        })


async def broadcast_to_group(db: AsyncSession, group_id: uuid.UUID, event_type: str, data: dict, exclude_user_id: uuid.UUID = None):
    """Broadcast an SSE event to all members of a group."""
    result = await db.execute(
        select(Membership.user_id).where(
            and_(
                Membership.group_id == group_id,
                Membership.is_active == True
            )
        )
    )
    member_ids = [row[0] for row in result.all()]

    for member_id in member_ids:
        if exclude_user_id and member_id == exclude_user_id:
            continue
        await send_sse_event(member_id, event_type, data)
