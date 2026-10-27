from __future__ import annotations

import os
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.auth.passwords import hash_password
from app.db.database import SessionLocal
from app.db.models import (
    EXPENSE_CATEGORIES,
    PAYMENT_METHODS,
    Donation,
    DonationPayment,
    Donor,
    Expense,
    Project,
    User,
    compute_donation_status,
)


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

DEMO_PROJECT_COUNT = 100
DEMO_DONOR_COUNT = 1500
# Rough pledges so most donors appear on at least one project.
DEMO_DONATION_COUNT = 4200
EXPENSES_PER_PROJECT = (4, 12)

EXPENSE_TITLES = (
    "Site materials purchase",
    "Volunteer transport",
    "Local contractor fees",
    "Printing & outreach flyers",
    "Warehouse storage rent",
    "Field staff stipend",
    "Utility bills",
    "Medical supplies restock",
    "Equipment hire",
    "Community event catering",
    "Permit & admin fees",
    "Fuel for deliveries",
    "Training workshop costs",
    "Safety gear",
    "Internet & communications",
)

FIRST_NAMES = (
    "Amina", "Omar", "Fatima", "Hassan", "Layla", "Yusuf", "Sara", "Ibrahim",
    "Maryam", "Ali", "Noor", "Khalid", "Hana", "Bilal", "Zainab", "Adam",
    "Leila", "Karim", "Nadia", "Samir", "Rania", "Tariq", "Dina", "Malik",
    "Salma", "Idris", "Yasmin", "Farid", "Huda", "Jamal", "Maya", "Rashid",
    "Sofia", "Nabil", "Aisha", "Hamza", "Lina", "Zayd", "Mona", "Imran",
    "Elena", "Daniel", "Priya", "James", "Chen", "Maria", "Ahmed", "Grace",
)

LAST_NAMES = (
    "Hassan", "Ali", "Khan", "Ahmed", "Rahman", "Hussein", "Omar", "Farouk",
    "Abbas", "Nasir", "Saleh", "Karim", "Mahmoud", "Qureshi", "Begum", "Shah",
    "Patel", "Singh", "Nguyen", "Silva", "Garcia", "Brown", "Wilson", "Clarke",
    "Martin", "Dubois", "Schmidt", "Rossi", "Costa", "Novak", "Ivanov", "Kim",
)

PROJECT_THEMES = (
    "Clean Water Wells",
    "School Renovation",
    "Orphan Sponsorship",
    "Ramadan Food Baskets",
    "Medical Clinic Support",
    "Winter Clothing Drive",
    "Mosque Community Centre",
    "Emergency Relief Fund",
    "Youth Education Grants",
    "Women Livelihood Kits",
    "Disability Aid Programme",
    "Refugee Housing Support",
    "Agricultural Tools Fund",
    "Quran Learning Centre",
    "Hospital Equipment Drive",
    "Village Solar Lighting",
    "Microfinance Seed Grants",
    "Disaster Response Pack",
    "Elderly Care Outreach",
    "Sports for Youth",
)

REGIONS = (
    "North District",
    "East Corridor",
    "Coastal Towns",
    "Highland Villages",
    "Central City",
    "Border Settlements",
    "River Communities",
    "Desert Outposts",
    "Island Parishes",
    "Urban Suburbs",
)


def seed_defaults():
    from app.db.repository import archive_completed_projects

    with SessionLocal.begin() as session:
        exists = session.scalar(
            select(User).where(User.username == DEFAULT_ADMIN_USERNAME)
        )
        if exists is None:
            session.add(
                User(
                    username=DEFAULT_ADMIN_USERNAME,
                    password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                    full_name="System Administrator",
                    role="admin",
                    is_active=True,
                    must_change_password=True,
                )
            )
    archive_completed_projects()
    # Production-safe default: never load demo data unless explicitly enabled.
    if _demo_seed_enabled():
        seed_demo_data()


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _demo_seed_enabled() -> bool:
    """Demo data is OFF by default. Enable with NGO_SEED_DEMO=1.

    Legacy: NGO_SKIP_DEMO_SEED=1 still forces skip (tests / old scripts).
    """
    if _env_flag("NGO_SKIP_DEMO_SEED"):
        return False
    return _env_flag("NGO_SEED_DEMO")


def seed_demo_data(*, force: bool = False) -> dict[str, int]:
    """Ensure demo volume: 100+ projects, 1500+ donors, pledges, and expenses.

    Call with force=True from a developer script, or set NGO_SEED_DEMO=1.
    """
    if not force and not _demo_seed_enabled():
        return {"projects": 0, "donors": 0, "donations": 0, "expenses": 0, "added": 0}
    rng = random.Random(20261021)
    today = date.today()

    with SessionLocal.begin() as session:
        project_count = session.scalar(select(func.count()).select_from(Project)) or 0
        donor_count = session.scalar(select(func.count()).select_from(Donor)) or 0
        donation_count = session.scalar(select(func.count()).select_from(Donation)) or 0
        expense_count = session.scalar(select(func.count()).select_from(Expense)) or 0
        projects_with_expenses = (
            session.scalar(
                select(func.count(func.distinct(Expense.project_id)))
            )
            or 0
        )

        already_complete = (
            not force
            and project_count >= DEMO_PROJECT_COUNT
            and donor_count >= DEMO_DONOR_COUNT
            and donation_count >= DEMO_DONATION_COUNT
            and projects_with_expenses >= project_count
            and project_count > 0
        )
        if already_complete:
            return {
                "projects": project_count,
                "donors": donor_count,
                "donations": donation_count,
                "expenses": expense_count,
                "added": 0,
            }

        projects = _ensure_projects(session, rng, today, project_count)
        donors = _ensure_donors(session, rng, donor_count)
        added_donations = _ensure_donations(
            session, rng, today, projects, donors, donation_count
        )
        added_expenses = _ensure_expenses(session, rng, today, projects)

        return {
            "projects": len(projects),
            "donors": len(donors),
            "donations": (donation_count or 0) + added_donations,
            "expenses": (expense_count or 0) + added_expenses,
            "added": added_donations + added_expenses,
        }


def _ensure_projects(session, rng: random.Random, today: date, existing: int):
    projects = list(session.scalars(select(Project).order_by(Project.id)).all())
    need = max(0, DEMO_PROJECT_COUNT - existing)
    years = list(range(today.year - 4, today.year + 1))

    for i in range(need):
        year = rng.choice(years)
        theme = rng.choice(PROJECT_THEMES)
        region = rng.choice(REGIONS)
        seq = existing + i + 1
        name = f"{theme} {year} — {region} #{seq}"

        start = date(year, rng.randint(1, 12), rng.randint(1, 28))
        # Campaigns span roughly one year from start.
        end = start + timedelta(days=365)
        created = datetime(start.year, start.month, start.day, 9, 0, 0)

        if end < today and rng.random() < 0.72:
            status = "Archived"
        elif start > today:
            status = "Active"
        else:
            status = rng.choices(
                ["Active", "On hold", "Archived"],
                weights=[65, 15, 20],
            )[0]

        target = Decimal(str(rng.randint(8_000, 250_000)))
        project = Project(
            name=name,
            description=(
                f"Year-long fundraising campaign for {theme.lower()} in {region}. "
                f"Campaign window {start.isoformat()} → {end.isoformat()}."
            ),
            target_amount=target,
            status=status,
            created_at=created,
        )
        # stash campaign window on the instance for donation dating
        project._campaign_start = start  # type: ignore[attr-defined]
        project._campaign_end = min(end, today)  # type: ignore[attr-defined]
        session.add(project)
        projects.append(project)

    session.flush()

    # Attach campaign windows for existing projects that lack them.
    for project in projects:
        if not hasattr(project, "_campaign_start"):
            created = project.created_at.date() if project.created_at else today
            start = created
            end = start + timedelta(days=365)
            project._campaign_start = start  # type: ignore[attr-defined]
            project._campaign_end = min(end, today) if start <= today else start  # type: ignore[attr-defined]

    return projects


def _ensure_donors(session, rng: random.Random, existing: int):
    donors = list(session.scalars(select(Donor).order_by(Donor.id)).all())
    need = max(0, DEMO_DONOR_COUNT - existing)
    new_donors: list[Donor] = []

    for i in range(need):
        n = existing + i + 1
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        name = f"{first} {last}"
        if rng.random() < 0.35:
            name = f"{name} {n}"
        email = f"{first.lower()}.{last.lower()}{n}@example.org"
        phone = f"+44 7{rng.randint(100, 999)} {rng.randint(100000, 999999)}"
        new_donors.append(
            Donor(
                name=name,
                email=email,
                phone=phone,
                address=f"{rng.randint(1, 220)} {rng.choice(REGIONS)} Road",
                notes="Demo donor",
            )
        )

    if new_donors:
        session.add_all(new_donors)
        session.flush()
        donors.extend(new_donors)

    return donors


def _ensure_donations(
    session,
    rng: random.Random,
    today: date,
    projects: list[Project],
    donors: list[Donor],
    existing_donations: int,
) -> int:
    need = max(0, DEMO_DONATION_COUNT - (existing_donations or 0))
    if need <= 0 or not projects or not donors:
        return 0

    batch: list[Donation] = []
    for _ in range(need):
        project = rng.choice(projects)
        donor = rng.choice(donors)
        pledged = Decimal(str(rng.randint(5, 1000)))

        roll = rng.random()
        if roll < 0.42:
            paid = pledged  # Completed
        elif roll < 0.78:
            # Remaining — partial payment
            if pledged <= 5:
                paid = Decimal("1.00")
            else:
                paid = Decimal(str(rng.randint(1, int(pledged) - 1)))
        else:
            paid = Decimal("0.00")  # Pending

        start: date = getattr(project, "_campaign_start", today - timedelta(days=180))
        end: date = getattr(project, "_campaign_end", today)
        if end < start:
            end = start
        span = (end - start).days
        donation_day = start + timedelta(days=rng.randint(0, max(span, 0)))
        if donation_day > today:
            donation_day = today

        method = rng.choice(PAYMENT_METHODS)
        ref = f"REF-{rng.randint(100000, 999999)}"
        donation = Donation(
            donor_id=donor.id,
            project_id=project.id,
            pledged_amount=pledged,
            paid_amount=paid,
            status=compute_donation_status(pledged, paid),
            donation_date=donation_day,
            payment_method=method,
            reference=ref,
            notes="",
        )
        batch.append(donation)

        if len(batch) >= 500:
            session.add_all(batch)
            session.flush()
            _seed_payments_for(session, batch, rng)
            batch.clear()

    if batch:
        session.add_all(batch)
        session.flush()
        _seed_payments_for(session, batch, rng)

    return need


def _seed_payments_for(session, donations: list[Donation], rng: random.Random) -> None:
    payments: list[DonationPayment] = []
    receivers = ("Front desk", "Finance officer", "Project lead", "Volunteer desk")
    for donation in donations:
        paid = Decimal(str(donation.paid_amount))
        if paid <= 0:
            continue
        # One installment for completed/pending-partial seed rows.
        payments.append(
            DonationPayment(
                donation_id=donation.id,
                amount=paid,
                payment_date=donation.donation_date,
                payment_method=donation.payment_method,
                received_by=rng.choice(receivers),
                reference=donation.reference or "",
                notes="Demo payment",
            )
        )
    if payments:
        session.add_all(payments)
        session.flush()


def _ensure_expenses(
    session,
    rng: random.Random,
    today: date,
    projects: list[Project],
) -> int:
    """Give every project a handful of expenses inside its campaign year."""
    if not projects:
        return 0

    already = set(
        session.scalars(select(Expense.project_id).distinct()).all()
    )
    batch: list[Expense] = []
    added = 0

    for project in projects:
        if project.id in already:
            continue

        start: date = getattr(project, "_campaign_start", today - timedelta(days=180))
        end: date = getattr(project, "_campaign_end", today)
        if end < start:
            end = start
        span = (end - start).days

        count = rng.randint(*EXPENSES_PER_PROJECT)
        for _ in range(count):
            day = start + timedelta(days=rng.randint(0, max(span, 0)))
            if day > today:
                day = today
            amount = Decimal(str(rng.randint(25, 4_500)))
            batch.append(
                Expense(
                    project_id=project.id,
                    title=rng.choice(EXPENSE_TITLES),
                    category=rng.choice(EXPENSE_CATEGORIES),
                    amount=amount,
                    expense_date=day,
                    notes="Demo expense",
                )
            )
            added += 1

        if len(batch) >= 400:
            session.add_all(batch)
            session.flush()
            batch.clear()

    if batch:
        session.add_all(batch)
        session.flush()

    return added
