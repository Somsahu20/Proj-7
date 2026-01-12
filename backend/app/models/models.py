import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Integer,
    ForeignKey, Numeric, Date, Enum as SQLEnum, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class MembershipRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class SplitType(str, enum.Enum):
    EQUAL = "equal"
    UNEQUAL = "unequal"
    SHARES = "shares"
    PERCENTAGE = "percentage"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    VOTING = "voting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class FriendshipStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    BLOCKED = "blocked"


# ==================== USERS ====================
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    notification_preferences = Column(JSONB, default=dict)
    reliability_score = Column(Integer, default=50)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    memberships = relationship("Membership", back_populates="user", foreign_keys="Membership.user_id")
    created_groups = relationship("Group", back_populates="creator", foreign_keys="Group.created_by_id")
    expenses_paid = relationship("Expense", back_populates="payer", foreign_keys="Expense.payer_id")
    expenses_created = relationship("Expense", back_populates="creator", foreign_keys="Expense.created_by_id")
    expense_splits = relationship("ExpenseSplit", back_populates="user")
    payments_made = relationship("Payment", back_populates="payer", foreign_keys="Payment.payer_id")
    payments_received = relationship("Payment", back_populates="receiver", foreign_keys="Payment.receiver_id")
    notifications = relationship("Notification", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    reactions = relationship("Reaction", back_populates="user")
    activities = relationship("ActivityLog", back_populates="user")


# ==================== GROUPS ====================
class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_archived = Column(Boolean, default=False)
    is_friend_group = Column(Boolean, default=False)  # Hidden group for friend expenses
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    settings = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="created_groups", foreign_keys=[created_by_id])
    memberships = relationship("Membership", back_populates="group")
    expenses = relationship("Expense", back_populates="group")
    payments = relationship("Payment", back_populates="group")
    invitations = relationship("Invitation", back_populates="group")
    activities = relationship("ActivityLog", back_populates="group")


# ==================== MEMBERSHIPS ====================
class Membership(Base):
    __tablename__ = "memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="member", nullable=False)
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    left_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_memberships_user_group"),
        CheckConstraint("role IN ('admin', 'member')", name="chk_memberships_role"),
    )

    # Relationships
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    group = relationship("Group", back_populates="memberships")
    invited_by = relationship("User", foreign_keys=[invited_by_id])


# ==================== INVITATIONS ====================
class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(20), default="pending")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    declined_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="invitations")
    invited_by = relationship("User", foreign_keys=[invited_by_id])


# ==================== EXPENSES ====================
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    payer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    split_type = Column(String(20), nullable=False)
    category = Column(String(50), nullable=True)
    notes = Column(String(500), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_status = Column(String(20), default="approved")
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_expenses_positive_amount"),
        CheckConstraint("split_type IN ('equal', 'unequal', 'shares', 'percentage')", name="chk_expenses_split_type"),
    )

    # Relationships
    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", back_populates="expenses_paid", foreign_keys=[payer_id])
    creator = relationship("User", back_populates="expenses_created", foreign_keys=[created_by_id])
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="expense", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="expense", cascade="all, delete-orphan")


# ==================== EXPENSE SPLITS ====================
class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    shares = Column(Integer, nullable=True)
    percentage = Column(Numeric(5, 2), nullable=True)
    is_settled = Column(Boolean, default=False)
    settled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", name="uq_splits_expense_user"),
    )

    # Relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="expense_splits")


# ==================== PAYMENTS ====================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    payer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(200), nullable=True)
    payment_method = Column(String(50), nullable=True)
    date = Column(Date, nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejected_reason = Column(String(500), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("payer_id != receiver_id", name="chk_payments_different_users"),
        CheckConstraint("amount > 0", name="chk_payments_positive_amount"),
        CheckConstraint("status IN ('pending', 'confirmed', 'rejected', 'cancelled', 'disputed')", name="chk_payments_status"),
    )

    # Relationships
    group = relationship("Group", back_populates="payments")
    payer = relationship("User", back_populates="payments_made", foreign_keys=[payer_id])
    receiver = relationship("User", back_populates="payments_received", foreign_keys=[receiver_id])
    proofs = relationship("PaymentProof", back_populates="payment", cascade="all, delete-orphan")


# ==================== PAYMENT PROOFS ====================
class PaymentProof(Base):
    __tablename__ = "payment_proofs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    payment = relationship("Payment", back_populates="proofs")


# ==================== NOTIFICATIONS ====================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(JSONB, default=dict)
    action_url = Column(String(500), nullable=True)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")


# ==================== COMMENTS ====================
class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    mentions = Column(JSONB, default=list)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    expense = relationship("Expense", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")


# ==================== REACTIONS ====================
class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    emoji = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", "emoji", name="uq_reactions_expense_user_emoji"),
    )

    # Relationships
    expense = relationship("Expense", back_populates="reactions")
    user = relationship("User", back_populates="reactions")


# ==================== ACTIVITY LOG ====================
class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    data = Column(JSONB, default=dict)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="activities")
    user = relationship("User", back_populates="activities")


# ==================== DISPUTES ====================
class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    opened_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    evidence_urls = Column(JSONB, default=list)
    status = Column(String(20), default="open")
    resolution = Column(String(20), nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    voting_ends_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    expense = relationship("Expense", foreign_keys=[expense_id])
    payment = relationship("Payment", foreign_keys=[payment_id])
    opened_by = relationship("User", foreign_keys=[opened_by_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    votes = relationship("DisputeVote", back_populates="dispute", cascade="all, delete-orphan")


# ==================== DISPUTE VOTES ====================
class DisputeVote(Base):
    __tablename__ = "dispute_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vote = Column(String(20), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("dispute_id", "user_id", name="uq_dispute_votes_user"),
    )

    # Relationships
    dispute = relationship("Dispute", back_populates="votes")
    user = relationship("User", foreign_keys=[user_id])


# ==================== EXPENSE TEMPLATES ====================
class ExpenseTemplate(Base):
    __tablename__ = "expense_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=True)
    category = Column(String(50), nullable=True)
    split_type = Column(String(20), nullable=True)
    split_data = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    group = relationship("Group", foreign_keys=[group_id])


# ==================== FRIENDSHIPS ====================
class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    addressee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    friend_group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)  # Hidden group for expenses
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
        CheckConstraint("requester_id != addressee_id", name="chk_friendship_different_users"),
        CheckConstraint("status IN ('pending', 'accepted', 'declined', 'blocked')", name="chk_friendship_status"),
    )

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], backref="friend_requests_sent")
    addressee = relationship("User", foreign_keys=[addressee_id], backref="friend_requests_received")
    friend_group = relationship("Group", foreign_keys=[friend_group_id])
