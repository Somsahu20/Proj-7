from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Dict
from decimal import Decimal
from collections import defaultdict
import uuid

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models import User, Group, Membership, Expense, ExpenseSplit, Payment
from app.schemas import (
    BalanceResponse, GroupBalanceSummary, UserBalance,
    SettlementSuggestion, GroupSettlementResponse, DebtSimplificationResult
)

router = APIRouter(prefix="/balances", tags=["Balances"])


async def get_group_balances(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID) -> Dict[uuid.UUID, Decimal]:
    """Calculate net balances for all users in a group relative to the given user."""
    balances = defaultdict(Decimal)

    # Get expenses where user paid
    paid_result = await db.execute(
        select(ExpenseSplit.user_id, func.sum(ExpenseSplit.amount))
        .join(Expense, Expense.id == ExpenseSplit.expense_id)
        .where(
            and_(
                Expense.group_id == group_id,
                Expense.payer_id == user_id,
                Expense.is_deleted == False,
                ExpenseSplit.user_id != user_id
            )
        )
        .group_by(ExpenseSplit.user_id)
    )
    for other_user_id, amount in paid_result.all():
        balances[other_user_id] += amount  # They owe user

    # Get expenses where user owes
    owed_result = await db.execute(
        select(Expense.payer_id, func.sum(ExpenseSplit.amount))
        .join(ExpenseSplit, ExpenseSplit.expense_id == Expense.id)
        .where(
            and_(
                Expense.group_id == group_id,
                ExpenseSplit.user_id == user_id,
                Expense.is_deleted == False,
                Expense.payer_id != user_id
            )
        )
        .group_by(Expense.payer_id)
    )
    for other_user_id, amount in owed_result.all():
        balances[other_user_id] -= amount  # User owes them

    # Get confirmed payments made by user
    payments_made_result = await db.execute(
        select(Payment.receiver_id, func.sum(Payment.amount))
        .where(
            and_(
                Payment.group_id == group_id,
                Payment.payer_id == user_id,
                Payment.status == "confirmed"
            )
        )
        .group_by(Payment.receiver_id)
    )
    for other_user_id, amount in payments_made_result.all():
        balances[other_user_id] += amount  # Increases what they owe (reduces what user owes)

    # Get confirmed payments received by user
    payments_received_result = await db.execute(
        select(Payment.payer_id, func.sum(Payment.amount))
        .where(
            and_(
                Payment.group_id == group_id,
                Payment.receiver_id == user_id,
                Payment.status == "confirmed"
            )
        )
        .group_by(Payment.payer_id)
    )
    for other_user_id, amount in payments_received_result.all():
        balances[other_user_id] -= amount  # Reduces what they owe

    return balances


async def get_all_group_debts(db: AsyncSession, group_id: uuid.UUID) -> List[Dict]:
    """Get all debts in a group (for simplification algorithm)."""
    # Net balance for each user
    user_balances = defaultdict(Decimal)

    # Get all expense splits
    splits_result = await db.execute(
        select(Expense.payer_id, ExpenseSplit.user_id, func.sum(ExpenseSplit.amount))
        .join(ExpenseSplit, ExpenseSplit.expense_id == Expense.id)
        .where(
            and_(
                Expense.group_id == group_id,
                Expense.is_deleted == False
            )
        )
        .group_by(Expense.payer_id, ExpenseSplit.user_id)
    )

    for payer_id, debtor_id, amount in splits_result.all():
        if payer_id != debtor_id:
            user_balances[payer_id] += amount  # Payer is owed
            user_balances[debtor_id] -= amount  # Debtor owes

    # Account for confirmed payments
    payments_result = await db.execute(
        select(Payment.payer_id, Payment.receiver_id, func.sum(Payment.amount))
        .where(
            and_(
                Payment.group_id == group_id,
                Payment.status == "confirmed"
            )
        )
        .group_by(Payment.payer_id, Payment.receiver_id)
    )

    for payer_id, receiver_id, amount in payments_result.all():
        user_balances[payer_id] += amount  # Payer paid off debt
        user_balances[receiver_id] -= amount  # Receiver got paid

    return dict(user_balances)


def simplify_debts(balances: Dict[uuid.UUID, Decimal]) -> List[Dict]:
    """
    Simplify debts using minimum cash flow algorithm.
    Returns list of {from_user_id, to_user_id, amount} transactions.
    """
    # Separate into creditors and debtors
    creditors = []  # (user_id, amount_owed_to_them)
    debtors = []    # (user_id, amount_they_owe)

    for user_id, balance in balances.items():
        if balance > Decimal("0.01"):
            creditors.append([user_id, balance])
        elif balance < Decimal("-0.01"):
            debtors.append([user_id, -balance])

    # Sort by amount (largest first)
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    settlements = []

    while creditors and debtors:
        creditor = creditors[0]
        debtor = debtors[0]

        amount = min(creditor[1], debtor[1])

        if amount > Decimal("0.01"):
            settlements.append({
                "from_user_id": debtor[0],
                "to_user_id": creditor[0],
                "amount": amount
            })

        creditor[1] -= amount
        debtor[1] -= amount

        if creditor[1] < Decimal("0.01"):
            creditors.pop(0)
        if debtor[1] < Decimal("0.01"):
            debtors.pop(0)

    return settlements


@router.get("", response_model=BalanceResponse)
async def get_my_balances(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's balances across all groups."""
    # Get user's groups
    memberships_result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.group))
        .where(
            and_(
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
    )
    memberships = memberships_result.scalars().all()

    group_balances = []
    total_you_are_owed = Decimal(0)
    total_you_owe = Decimal(0)

    for membership in memberships:
        if membership.group.is_deleted:
            continue

        balances = await get_group_balances(db, membership.group_id, current_user.id)

        # Get user info for each balance
        user_balances = []
        group_net = Decimal(0)

        for other_user_id, balance in balances.items():
            if abs(balance) < Decimal("0.01"):
                continue

            user_result = await db.execute(
                select(User).where(User.id == other_user_id)
            )
            other_user = user_result.scalar_one_or_none()

            if other_user:
                user_balances.append(UserBalance(
                    user_id=other_user_id,
                    user_name=other_user.name,
                    user_email=other_user.email,
                    balance=balance,
                    profile_picture=other_user.profile_picture
                ))
                group_net += balance

                if balance > 0:
                    total_you_are_owed += balance
                else:
                    total_you_owe += abs(balance)

        if user_balances:
            group_balances.append(GroupBalanceSummary(
                group_id=membership.group_id,
                group_name=membership.group.name,
                your_total_balance=group_net,
                balances=user_balances
            ))

    return BalanceResponse(
        total_balance=total_you_are_owed - total_you_owe,
        you_are_owed=total_you_are_owed,
        you_owe=total_you_owe,
        group_balances=group_balances
    )


@router.get("/group/{group_id}", response_model=GroupBalanceSummary)
async def get_group_balance(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get balances for a specific group."""
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

    balances = await get_group_balances(db, group_id, current_user.id)

    user_balances = []
    group_net = Decimal(0)

    for other_user_id, balance in balances.items():
        if abs(balance) < Decimal("0.01"):
            continue

        user_result = await db.execute(
            select(User).where(User.id == other_user_id)
        )
        other_user = user_result.scalar_one_or_none()

        if other_user:
            user_balances.append(UserBalance(
                user_id=other_user_id,
                user_name=other_user.name,
                user_email=other_user.email,
                balance=balance,
                profile_picture=other_user.profile_picture
            ))
            group_net += balance

    return GroupBalanceSummary(
        group_id=group_id,
        group_name=membership.group.name,
        your_total_balance=group_net,
        balances=user_balances
    )


@router.get("/group/{group_id}/settlements", response_model=GroupSettlementResponse)
async def get_settlement_suggestions(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get optimized settlement suggestions for a group."""
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

    # Get all balances
    all_balances = await get_all_group_debts(db, group_id)

    # Count original transactions (before simplification)
    # This is the count of non-zero balance pairs
    original_count = sum(1 for b in all_balances.values() if abs(b) > Decimal("0.01"))

    # Simplify
    simplified = simplify_debts(all_balances)

    # Get user names
    suggestions = []
    for settlement in simplified:
        from_user_result = await db.execute(
            select(User).where(User.id == settlement["from_user_id"])
        )
        to_user_result = await db.execute(
            select(User).where(User.id == settlement["to_user_id"])
        )
        from_user = from_user_result.scalar_one()
        to_user = to_user_result.scalar_one()

        suggestions.append(SettlementSuggestion(
            from_user_id=settlement["from_user_id"],
            from_user_name=from_user.name,
            to_user_id=settlement["to_user_id"],
            to_user_name=to_user.name,
            amount=settlement["amount"]
        ))

    return GroupSettlementResponse(
        group_id=group_id,
        group_name=membership.group.name,
        suggestions=suggestions,
        total_transactions=len(suggestions),
        original_transactions=original_count
    )


@router.get("/simplify/{group_id}", response_model=DebtSimplificationResult)
async def simplify_group_debts(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get debt simplification details for a group."""
    # Check membership
    membership_result = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == current_user.id,
                Membership.is_active == True
            )
        )
    )
    if not membership_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    # Get all balances
    all_balances = await get_all_group_debts(db, group_id)

    # Get user info for original debts
    original_debts = []
    for user_id, balance in all_balances.items():
        if abs(balance) > Decimal("0.01"):
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one()
            original_debts.append({
                "user_id": str(user_id),
                "user_name": user.name,
                "balance": float(balance)
            })

    # Simplify
    simplified = simplify_debts(all_balances)

    # Get user names for simplified
    simplified_suggestions = []
    for settlement in simplified:
        from_user_result = await db.execute(
            select(User).where(User.id == settlement["from_user_id"])
        )
        to_user_result = await db.execute(
            select(User).where(User.id == settlement["to_user_id"])
        )
        from_user = from_user_result.scalar_one()
        to_user = to_user_result.scalar_one()

        simplified_suggestions.append(SettlementSuggestion(
            from_user_id=settlement["from_user_id"],
            from_user_name=from_user.name,
            to_user_id=settlement["to_user_id"],
            to_user_name=to_user.name,
            amount=settlement["amount"]
        ))

    # Calculate transactions saved
    # Original would be n*(n-1)/2 worst case, but we use actual debt count
    original_transaction_count = len([b for b in all_balances.values() if abs(b) > Decimal("0.01")])

    return DebtSimplificationResult(
        original_debts=original_debts,
        simplified_debts=simplified_suggestions,
        transactions_saved=max(0, original_transaction_count - len(simplified_suggestions))
    )
