from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import cast
from decimal import Decimal
from datetime import date, timedelta
import uuid

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models import User, Group, Membership, Expense, ExpenseSplit
from app.schemas import (
    CategorySpending, SpendingDataPoint, MemberContribution, FriendSpending,
    GroupAnalyticsResponse, FriendsAnalyticsResponse
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def calculate_date_range(period: str) -> tuple[date, date]:
    """Calculate start and end dates based on period string."""
    
    end_day = date.today()
    start_date = end_day
    if period == "7d":
        start_date -= timedelta(days=6)
    elif period == "30d":
        start_date -= timedelta(days=29)
    elif period == "3m":
        start_date -= timedelta(days=89)
    elif period == "1y":
        start_date -= timedelta(days=364)

    return (start_date, end_day)


@router.get("/group/{group_id}", response_model=GroupAnalyticsResponse)
async def get_group_analytics(
    group_id: uuid.UUID,
    period: str = Query("30d", pattern="^(7d|30d|3m|1y)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific group."""
    # Check membership
    membership_result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.group))
        .where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
    )
    membership = membership_result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    # Calculate date range
    start_date, end_date = calculate_date_range(period)

    # Get expenses in date range
    base_filter = and_(
        Expense.group_id == group_id,
        Expense.is_deleted == False,
        Expense.date >= start_date,
        Expense.date <= end_date
    )

    # 1. Category breakdown
    category_expr = func.coalesce(func.nullif(func.trim(Expense.category), ''), 'Other')
    category_result = await db.execute(
        select(
            category_expr.label('category'),
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('expense_count')
        )
        .where(base_filter)
        .group_by(category_expr)
        .order_by(func.sum(Expense.amount).desc())
    )
    category_data = category_result.all()

    total_spending: Decimal = sum(
        ((Decimal(row.total) if row.total is not None else Decimal(0)) for row in category_data),
        Decimal(0),
    ) if category_data else Decimal(0)
    expense_count = sum((row.expense_count or 0) for row in category_data) if category_data else 0

    category_breakdown = []
    for row in category_data:
        row_total = Decimal(row.total) if row.total is not None else Decimal(0)
        percentage: Decimal = (row_total / total_spending * Decimal("100")) if total_spending > 0 else Decimal(0)
        category_breakdown.append(CategorySpending(
            category=row.category or 'Other',
            amount=row_total,
            percentage=percentage.quantize(Decimal("0.1")),
            expense_count=row.expense_count or 0
        ))

    top_category = category_breakdown[0].category if category_breakdown else None

    # 2. Spending over time
    time_result = await db.execute(
        select(
            Expense.date,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('expense_count')
        )
        .where(base_filter)
        .group_by(Expense.date)
        .order_by(Expense.date)
    )
    time_data = time_result.all()

    spending_over_time = [
        SpendingDataPoint(
            date=row.date,
            amount=row.total or Decimal(0),
            expense_count=row.expense_count or 0
        )
        for row in time_data
    ]

    # 3. Member contributions
    # Get all group members
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
    member_ids = [cast(uuid.UUID, m.user_id) for m in members]
    member_map = {cast(uuid.UUID, m.user_id): m.user for m in members}

    # Total paid by each member
    paid_result = await db.execute(
        select(
            Expense.payer_id,
            func.sum(Expense.amount).label('total_paid')
        )
        .where(base_filter)
        .group_by(Expense.payer_id)
    )
    paid_by_user = {row.payer_id: (row.total_paid or Decimal(0)) for row in paid_result.all()}

    # Total share for each member
    share_result = await db.execute(
        select(
            ExpenseSplit.user_id,
            func.sum(ExpenseSplit.amount).label('total_share')
        )
        .join(Expense, Expense.id == ExpenseSplit.expense_id)
        .where(base_filter)
        .group_by(ExpenseSplit.user_id)
    )
    share_by_user = {row.user_id: (row.total_share or Decimal(0)) for row in share_result.all()}

    member_contributions = []
    for member_id in member_ids:
        user = member_map.get(member_id)
        if not user:
            continue

        total_paid = paid_by_user.get(member_id, Decimal(0))
        total_share = share_by_user.get(member_id, Decimal(0))

        # Only include members with activity
        if total_paid > 0 or total_share > 0:
            member_contributions.append(MemberContribution(
                user_id=member_id,
                user_name=user.name,
                profile_picture=user.profile_picture,
                total_paid=total_paid,
                total_share=total_share,
                net_contribution=total_paid - total_share
            ))

    # Sort by total_paid descending
    member_contributions.sort(key=lambda x: x.total_paid, reverse=True)

    average_expense = total_spending / expense_count if expense_count > 0 else Decimal(0)
    average_expense = average_expense.quantize(Decimal("0.01"))

    return GroupAnalyticsResponse(
        group_id=group_id,
        group_name=membership.group.name,
        period=period,
        start_date=start_date,
        end_date=end_date,
        total_spending=total_spending,
        expense_count=expense_count,
        category_breakdown=category_breakdown,
        spending_over_time=spending_over_time,
        member_contributions=member_contributions,
        average_expense=average_expense,
        top_category=top_category
    )


@router.get("/friends", response_model=FriendsAnalyticsResponse)
async def get_friends_analytics(
    period: str = Query("30d", pattern="^(7d|30d|3m|1y)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics across all friend expenses."""
    # Calculate date range
    start_date, end_date = calculate_date_range(period)

    # Get all friend groups (is_friend_group=True) where user is a member
    friend_groups_result = await db.execute(
        select(Membership.group_id)
        .join(Group, Group.id == Membership.group_id)
        .where(
            and_(
                Membership.user_id == current_user.id,
                Membership.is_active == True,
                or_(
                    Group.is_friend_group == True,
                    Group.category == "friends",
                ),
                Group.is_deleted == False
            )
        )
    )
    friend_group_ids = [row[0] for row in friend_groups_result.all()]

    if not friend_group_ids:
        # No friend groups - return empty analytics
        return FriendsAnalyticsResponse(
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_spending=Decimal(0),
            expense_count=0,
            category_breakdown=[],
            spending_over_time=[],
            friend_breakdown=[],
            average_expense=Decimal(0),
            top_category=None
        )

    # Base filter for friend expenses
    base_filter = and_(
        Expense.group_id.in_(friend_group_ids),
        Expense.is_deleted == False,
        Expense.date >= start_date,
        Expense.date <= end_date
    )

    # 1. Category breakdown
    category_expr = func.coalesce(func.nullif(func.trim(Expense.category), ''), 'Other')
    category_result = await db.execute(
        select(
            category_expr.label('category'),
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('expense_count')
        )
        .where(base_filter)
        .group_by(category_expr)
        .order_by(func.sum(Expense.amount).desc())
    )
    category_data = category_result.all()

    total_spending: Decimal = sum(
        ((Decimal(row.total) if row.total is not None else Decimal(0)) for row in category_data),
        Decimal(0),
    ) if category_data else Decimal(0)
    expense_count = sum((row.expense_count or 0) for row in category_data) if category_data else 0

    category_breakdown = []
    for row in category_data:
        row_total = Decimal(row.total) if row.total is not None else Decimal(0)
        percentage: Decimal = (row_total / total_spending * Decimal("100")) if total_spending > 0 else Decimal(0)
        category_breakdown.append(CategorySpending(
            category=row.category or 'Other',
            amount=row_total,
            percentage=percentage.quantize(Decimal("0.1")),
            expense_count=row.expense_count or 0
        ))

    top_category = category_breakdown[0].category if category_breakdown else None

    # 2. Spending over time
    time_result = await db.execute(
        select(
            Expense.date,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('expense_count')
        )
        .where(base_filter)
        .group_by(Expense.date)
        .order_by(Expense.date)
    )
    time_data = time_result.all()

    spending_over_time = [
        SpendingDataPoint(
            date=row.date,
            amount=row.total or Decimal(0),
            expense_count=row.expense_count or 0
        )
        for row in time_data
    ]

    # 3. Friend breakdown - spending per friend
    # Get spending grouped by friend group, then map to friend
    friend_spending_result = await db.execute(
        select(
            Expense.group_id,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('expense_count')
        )
        .where(base_filter)
        .group_by(Expense.group_id)
    )
    group_spending = {row.group_id: ((row.total or Decimal(0)), (row.expense_count or 0)) for row in friend_spending_result.all()}

    # Map group_id to friend user
    friend_breakdown = []
    for group_id in friend_group_ids:
        if group_id not in group_spending:
            continue

        total, count = group_spending[group_id]

        # Find the friend in this group (not current user)
        friend_result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.user))
            .where(
                and_(
                    Membership.group_id == group_id,
                    Membership.user_id != current_user.id,
                    Membership.is_active == True
                )
            )
        )
        friend_membership = friend_result.scalar_one_or_none()

        if friend_membership and friend_membership.user:
            friend = friend_membership.user
            friend_breakdown.append(FriendSpending(
                friend_id=friend.id,
                friend_name=friend.name,
                profile_picture=friend.profile_picture,
                total_spent=total,
                expense_count=count
            ))

    # Sort by total spent descending
    friend_breakdown.sort(key=lambda x: x.total_spent, reverse=True)

    average_expense = total_spending / expense_count if expense_count > 0 else Decimal(0)
    average_expense = average_expense.quantize(Decimal("0.01"))

    return FriendsAnalyticsResponse(
        period=period,
        start_date=start_date,
        end_date=end_date,
        total_spending=total_spending,
        expense_count=expense_count,
        category_breakdown=category_breakdown,
        spending_over_time=spending_over_time,
        friend_breakdown=friend_breakdown,
        average_expense=average_expense,
        top_category=top_category
    )
