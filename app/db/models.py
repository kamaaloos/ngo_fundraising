from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


user_projects = Table(
    "user_projects",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "project_id",
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


PAYMENT_METHODS = (
    "Cash",
    "Card",
    "Bank transfer",
    "Cheque",
    "Online",
    "Mobile money",
    "Other",
)
DONATION_STATUSES = ("Pending", "Remaining", "Completed")
# "Completed" is legacy and is normalized to Archived on save / startup.
PROJECT_STATUSES = ("Active", "On hold", "Archived")
PROJECT_STATUS_ARCHIVED = "Archived"
PROJECT_STATUS_COMPLETED_LEGACY = "Completed"
USER_ROLES = ("admin", "user")
EXPENSE_CATEGORIES = (
    "Operations",
    "Materials",
    "Travel",
    "Marketing",
    "Staff",
    "Utilities",
    "Other",
)


def compute_donation_status(pledged: Decimal, paid: Decimal) -> str:
    pledged = Decimal(str(pledged or 0))
    paid = Decimal(str(paid or 0))
    if paid <= 0:
        return "Pending"
    if paid < pledged:
        return "Remaining"
    return "Completed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), default="")
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    must_change_password: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    projects: Mapped[list[Project]] = relationship(
        secondary=user_projects,
        back_populates="users",
    )
    collections: Mapped[list[Donation]] = relationship(
        back_populates="collected_by",
        foreign_keys="Donation.collected_by_user_id",
    )

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def display_name(self) -> str:
        name = (self.full_name or "").strip()
        return name or self.username


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    target_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="Active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    donations: Mapped[list[Donation]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    expenses: Mapped[list[Expense]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    users: Mapped[list[User]] = relationship(
        secondary=user_projects,
        back_populates="projects",
    )

    @property
    def amount_raised(self) -> Decimal:
        """Actual funds received (sum of paid amounts)."""
        cached = getattr(self, "_agg_raised", None)
        if cached is not None:
            return cached
        return sum(
            (Decimal(str(d.paid_amount)) for d in self.donations),
            Decimal("0.00"),
        )

    @property
    def amount_pledged(self) -> Decimal:
        cached = getattr(self, "_agg_pledged", None)
        if cached is not None:
            return cached
        return sum(
            (Decimal(str(d.pledged_amount)) for d in self.donations),
            Decimal("0.00"),
        )

    @property
    def total_expenses(self) -> Decimal:
        cached = getattr(self, "_agg_expenses", None)
        if cached is not None:
            return cached
        return sum(
            (Decimal(str(e.amount)) for e in self.expenses),
            Decimal("0.00"),
        )

    @property
    def donation_count(self) -> int:
        cached = getattr(self, "_agg_donation_count", None)
        if cached is not None:
            return int(cached)
        return len(self.donations)

    @property
    def remaining_to_target(self) -> Decimal:
        rem = Decimal(str(self.target_amount)) - self.amount_raised
        return rem if rem > 0 else Decimal("0.00")

    @property
    def progress_percent(self) -> float:
        target = Decimal(str(self.target_amount))
        if target <= 0:
            return 0.0
        return min(100.0, float(self.amount_raised / target * 100))

    @property
    def fundraising_status(self) -> str:
        raised = self.amount_raised
        target = Decimal(str(self.target_amount))
        if raised <= 0:
            return "Not started"
        if raised < target:
            return "In progress"
        return "Fully funded"

    @property
    def unique_donor_count(self) -> int:
        cached = getattr(self, "_agg_donor_count", None)
        if cached is not None:
            return int(cached)
        return len({d.donor_id for d in self.donations})


class Donor(Base):
    """Global donor — can donate to many projects."""

    __tablename__ = "donors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(200), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    donations: Mapped[list[Donation]] = relationship(
        back_populates="donor", cascade="all, delete-orphan"
    )

    @property
    def total_pledged(self) -> Decimal:
        return sum(
            (Decimal(str(d.pledged_amount)) for d in self.donations),
            Decimal("0.00"),
        )

    @property
    def total_paid(self) -> Decimal:
        return sum(
            (Decimal(str(d.paid_amount)) for d in self.donations),
            Decimal("0.00"),
        )

    @property
    def total_remaining(self) -> Decimal:
        rem = self.total_pledged - self.total_paid
        return rem if rem > 0 else Decimal("0.00")

    @property
    def total_donated(self) -> Decimal:
        return self.total_paid

    @property
    def project_ids(self) -> set[int]:
        return {d.project_id for d in self.donations}


class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    donor_id: Mapped[int] = mapped_column(
        ForeignKey("donors.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    pledged_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    status: Mapped[str] = mapped_column(String(30), default="Pending")
    donation_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False
    )
    payment_method: Mapped[str] = mapped_column(String(50), default="Cash")
    reference: Mapped[str] = mapped_column(String(100), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    collected_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    donor: Mapped[Donor] = relationship(back_populates="donations")
    project: Mapped[Project] = relationship(back_populates="donations")
    collected_by: Mapped[User | None] = relationship(
        back_populates="collections",
        foreign_keys=[collected_by_user_id],
    )
    payments: Mapped[list[DonationPayment]] = relationship(
        back_populates="donation", cascade="all, delete-orphan"
    )

    @property
    def collector_label(self) -> str:
        if self.collected_by is not None:
            return self.collected_by.display_name
        return ""

    def sync_status(self) -> None:
        self.status = compute_donation_status(self.pledged_amount, self.paid_amount)

    @property
    def remaining_amount(self) -> Decimal:
        rem = Decimal(str(self.pledged_amount)) - Decimal(str(self.paid_amount))
        return rem if rem > 0 else Decimal("0.00")

    @property
    def payment_count(self) -> int:
        return len(self.payments)


class DonationPayment(Base):
    """One received installment toward a donation pledge."""

    __tablename__ = "donation_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    donation_id: Mapped[int] = mapped_column(
        ForeignKey("donations.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False
    )
    payment_method: Mapped[str] = mapped_column(String(50), default="Cash")
    received_by: Mapped[str] = mapped_column(String(150), default="")
    reference: Mapped[str] = mapped_column(String(100), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    donation: Mapped[Donation] = relationship(back_populates="payments")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="Other")
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    expense_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False
    )
    notes: Mapped[str] = mapped_column(Text, default="")

    project: Mapped[Project] = relationship(back_populates="expenses")
