from __future__ import annotations

from decimal import Decimal

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import selectinload

from app.auth.passwords import hash_password, verify_password
from app.auth.session import current_session
from app.db.access import (
    AccessDenied,
    accessible_project_ids,
    require_admin,
    require_auth,
    require_project_access,
)
from app.db.database import SessionLocal, get_app_meta, set_app_meta
from app.db.models import (
    Donation,
    DonationPayment,
    Donor,
    Expense,
    Project,
    User,
    PROJECT_STATUS_ARCHIVED,
    PROJECT_STATUS_COMPLETED_LEGACY,
    compute_donation_status,
)

ADMIN_RECOVERY_META_KEY = "admin_recovery_hash"


def _dec(value) -> Decimal:
    return Decimal(str(value or 0))


def _attach_project_aggregates(session, projects: list[Project]) -> None:
    if not projects:
        return
    ids = [p.id for p in projects]
    raised_rows = session.execute(
        select(
            Donation.project_id,
            func.coalesce(func.sum(Donation.paid_amount), 0),
            func.coalesce(func.sum(Donation.pledged_amount), 0),
            func.count(Donation.id),
            func.count(distinct(Donation.donor_id)),
        )
        .where(Donation.project_id.in_(ids))
        .group_by(Donation.project_id)
    ).all()
    expense_rows = session.execute(
        select(
            Expense.project_id,
            func.coalesce(func.sum(Expense.amount), 0),
        )
        .where(Expense.project_id.in_(ids))
        .group_by(Expense.project_id)
    ).all()
    raised_map = {
        pid: (_dec(paid), _dec(pledged), int(don_count), int(donor_count))
        for pid, paid, pledged, don_count, donor_count in raised_rows
    }
    expense_map = {pid: _dec(total) for pid, total in expense_rows}
    for project in projects:
        paid, pledged, don_count, donor_count = raised_map.get(
            project.id, (Decimal("0.00"), Decimal("0.00"), 0, 0)
        )
        project._agg_raised = paid  # type: ignore[attr-defined]
        project._agg_pledged = pledged  # type: ignore[attr-defined]
        project._agg_donation_count = don_count  # type: ignore[attr-defined]
        project._agg_donor_count = donor_count  # type: ignore[attr-defined]
        project._agg_expenses = expense_map.get(project.id, Decimal("0.00"))  # type: ignore[attr-defined]


# ---------- Auth / Users ----------

def authenticate(username: str, password: str) -> User | None:
    with SessionLocal() as session:
        user = session.scalar(
            select(User)
            .options(selectinload(User.projects))
            .where(User.username == username.strip())
        )
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        session.expunge(user)
        for project in user.projects:
            session.expunge(project)
        return user


def list_users() -> list[User]:
    require_admin()
    with SessionLocal() as session:
        users = session.scalars(
            select(User)
            .options(selectinload(User.projects))
            .order_by(User.username)
        ).all()
        for user in users:
            session.expunge(user)
            for project in user.projects:
                session.expunge(project)
        return list(users)


def list_collector_choices() -> list[User]:
    """Active staff users for the 'Collected by' picker (any signed-in role)."""
    require_auth()
    with SessionLocal() as session:
        users = session.scalars(
            select(User)
            .where(User.is_active.is_(True))
            .order_by(User.full_name, User.username)
        ).all()
        result = list(users)
        session.expunge_all()
        return result


def save_user(
    user_id: int | None,
    values: dict,
    project_ids: list[int] | None = None,
) -> int:
    require_admin()
    with SessionLocal.begin() as session:
        password = values.pop("password", None)
        values = dict(values)
        if user_id is None:
            if "must_change_password" not in values:
                values["must_change_password"] = bool(password)
            user = User(**values)
            if password:
                user.password_hash = hash_password(password)
            session.add(user)
            session.flush()
        else:
            user = session.get(User, user_id)
            if user is None:
                raise ValueError("User not found")
            for key, value in values.items():
                setattr(user, key, value)
            if password:
                user.password_hash = hash_password(password)
                user.must_change_password = False

        if project_ids is not None and user.role != "admin":
            projects = session.scalars(
                select(Project).where(Project.id.in_(project_ids or [-1]))
            ).all()
            user.projects = list(projects)
        elif user.role == "admin":
            user.projects = []

        session.flush()
        return user.id


def change_own_password(user_id: int, current_password: str, new_password: str) -> None:
    require_auth()
    if current_session.user_id != user_id and not current_session.is_admin:
        raise AccessDenied("You can only change your own password.")
    if len(new_password or "") < 8:
        raise ValueError("New password must be at least 8 characters.")
    with SessionLocal.begin() as session:
        user = session.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect.")
        user.password_hash = hash_password(new_password)
        user.must_change_password = False


def has_admin_recovery_key() -> bool:
    return bool(get_app_meta(ADMIN_RECOVERY_META_KEY))


def set_admin_recovery_key(recovery_key: str) -> None:
    """Store a hashed recovery key used to reset admin from the login screen."""
    require_auth()
    if not current_session.is_admin:
        raise AccessDenied("Only an admin can set the recovery key.")
    key = (recovery_key or "").strip()
    if len(key) < 8:
        raise ValueError("Recovery key must be at least 8 characters.")
    set_app_meta(ADMIN_RECOVERY_META_KEY, hash_password(key))


def verify_admin_recovery_key(recovery_key: str) -> bool:
    stored = get_app_meta(ADMIN_RECOVERY_META_KEY)
    if not stored:
        return False
    return verify_password((recovery_key or "").strip(), stored)


def reset_local_admin_password(
    *,
    temporary_password: str = "admin123",
    username: str = "admin",
    recovery_key: str | None = None,
    allow_unauthenticated_script: bool = False,
) -> tuple[str, str]:
    """Reset admin on this PC's local database.

    From the login UI, a valid recovery key is required.
    The support script may pass allow_unauthenticated_script=True (trusted
    operator with project/venv access).
    """
    if len(temporary_password or "") < 8:
        raise ValueError("Temporary password must be at least 8 characters.")

    if not allow_unauthenticated_script:
        if not has_admin_recovery_key():
            raise ValueError(
                "This install is not registered for recovery yet. "
                "Contact MayleSoft support with your Install ID, or ask "
                "support to run the offline reset script."
            )
        if not verify_admin_recovery_key(recovery_key or ""):
            raise ValueError("Recovery key is incorrect.")

    with SessionLocal.begin() as session:
        user = session.scalar(select(User).where(User.username == username))
        if user is None:
            user = session.scalar(select(User).where(User.role == "admin").limit(1))
        if user is None:
            raise ValueError("No admin user found in the database.")
        user.password_hash = hash_password(temporary_password)
        user.must_change_password = True
        user.is_active = True
        return user.username, temporary_password


def delete_user(user_id: int) -> None:
    require_admin()
    with SessionLocal.begin() as session:
        user = session.get(User, user_id)
        if user is None:
            return
        if user.role == "admin":
            admin_count = session.scalar(
                select(func.count()).select_from(User).where(User.role == "admin")
            )
            if admin_count <= 1:
                raise ValueError("Cannot delete the last admin account.")
        session.delete(user)


# ---------- Projects ----------

def archive_completed_projects() -> int:
    """Move legacy 'Completed' projects into Archived. Returns rows updated."""
    with SessionLocal.begin() as session:
        projects = session.scalars(
            select(Project).where(Project.status == PROJECT_STATUS_COMPLETED_LEGACY)
        ).all()
        for project in projects:
            project.status = PROJECT_STATUS_ARCHIVED
        return len(projects)


def normalize_project_status(status: str | None) -> str:
    value = (status or "Active").strip()
    if value == PROJECT_STATUS_COMPLETED_LEGACY:
        return PROJECT_STATUS_ARCHIVED
    return value


def list_projects(
    user: User | None = None,
    *,
    role: str | None = None,
    project_ids: list[int] | None = None,
    search: str = "",
    status: str | None = None,
    include_archived: bool = True,
    enforce_acl: bool = True,
) -> list[Project]:
    if enforce_acl:
        require_auth()

    with SessionLocal() as session:
        query = select(Project).order_by(Project.name)
        filters = []
        term = (search or "").strip()
        if term:
            like = f"%{term}%"
            filters.append(
                or_(Project.name.ilike(like), Project.description.ilike(like))
            )
        if status:
            filters.append(Project.status == normalize_project_status(status))
        elif not include_archived:
            filters.append(
                Project.status.notin_(
                    [PROJECT_STATUS_ARCHIVED, PROJECT_STATUS_COMPLETED_LEGACY]
                )
            )
        if filters:
            query = query.where(*filters)

        projects = list(session.scalars(query).all())

        effective_role = role
        allowed_ids = project_ids
        if user is not None:
            effective_role = user.role
            allowed_ids = [p.id for p in user.projects]
        elif enforce_acl and role is None and project_ids is None:
            effective_role = current_session.role
            allowed_ids = current_session.project_ids

        if effective_role is not None and effective_role != "admin":
            allowed = set(allowed_ids or [])
            projects = [p for p in projects if p.id in allowed]

        _attach_project_aggregates(session, projects)
        for project in projects:
            session.expunge(project)
        return projects


def get_project(project_id: int, *, enforce_acl: bool = True) -> Project | None:
    if enforce_acl:
        require_project_access(project_id)
    with SessionLocal() as session:
        project = session.scalar(
            select(Project)
            .options(selectinload(Project.users))
            .where(Project.id == project_id)
        )
        if project is None:
            return None
        _attach_project_aggregates(session, [project])
        session.expunge(project)
        return project


def save_project(project_id: int | None, values: dict) -> int:
    require_admin()
    values = dict(values)
    if "status" in values:
        values["status"] = normalize_project_status(values.get("status"))
    with SessionLocal.begin() as session:
        if project_id is None:
            project = Project(**values)
            session.add(project)
            session.flush()
            return project.id
        project = session.get(Project, project_id)
        if project is None:
            raise ValueError("Project not found")
        for key, value in values.items():
            setattr(project, key, value)
        return project.id


def delete_project(project_id: int) -> None:
    require_admin()
    with SessionLocal.begin() as session:
        project = session.get(Project, project_id)
        if project is not None:
            session.delete(project)


# ---------- Donors ----------

def list_donors(
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    project_id: int | None = None,
) -> tuple[list[Donor], int]:
    """List donors. Non-admins are scoped to accessible projects."""
    require_auth()
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    allowed = accessible_project_ids()
    if project_id is not None:
        require_project_access(project_id)
        scope_ids = [project_id]
    elif allowed is None:
        scope_ids = None  # admin, all donors
    else:
        scope_ids = allowed  # non-admin: donors linked to any assigned project

    with SessionLocal() as session:
        filters = []
        term = (search or "").strip()
        if term:
            like = f"%{term}%"
            filters.append(
                or_(
                    Donor.name.ilike(like),
                    Donor.email.ilike(like),
                    Donor.phone.ilike(like),
                )
            )
        if scope_ids is not None:
            if not scope_ids:
                return [], 0
            filters.append(
                Donor.id.in_(
                    select(Donation.donor_id).where(Donation.project_id.in_(scope_ids))
                )
            )

        count_query = select(func.count()).select_from(Donor)
        if filters:
            count_query = count_query.where(*filters)
        total = session.scalar(count_query) or 0

        query = (
            select(Donor)
            .options(selectinload(Donor.donations).selectinload(Donation.project))
            .order_by(Donor.name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if filters:
            query = query.where(*filters)

        donors = session.scalars(query).all()
        result = list(donors)
        for donor in result:
            session.expunge(donor)
        return result, int(total)


def list_all_donors() -> list[Donor]:
    """Donors available when recording a donation (authenticated).

    Non-admins only see donors linked to an assigned project, plus unused
    donors (no donations yet) so they can still record a first gift.
    """
    require_auth()
    allowed = accessible_project_ids()
    with SessionLocal() as session:
        query = select(Donor).order_by(Donor.name)
        if allowed is not None:
            unused = ~Donor.id.in_(select(Donation.donor_id).distinct())
            if allowed:
                linked = Donor.id.in_(
                    select(Donation.donor_id).where(Donation.project_id.in_(allowed))
                )
                query = query.where(or_(unused, linked))
            else:
                query = query.where(unused)
        donors = session.scalars(query).all()
        result = list(donors)
        for donor in result:
            session.expunge(donor)
        return result


def get_donor(donor_id: int) -> Donor | None:
    require_auth()
    with SessionLocal() as session:
        donor = session.scalar(
            select(Donor)
            .options(selectinload(Donor.donations).selectinload(Donation.project))
            .where(Donor.id == donor_id)
        )
        if donor is None:
            return None
        if not current_session.is_admin:
            allowed = set(current_session.project_ids)
            if not any(d.project_id in allowed for d in donor.donations):
                # Brand-new donor with no gifts yet: allow (e.g. just created).
                if donor.donations:
                    raise AccessDenied("You cannot view this donor.")
        session.expunge(donor)
        return donor


def donor_project_summary(donor_id: int) -> dict:
    require_auth()
    with SessionLocal() as session:
        donor = session.scalar(
            select(Donor)
            .options(selectinload(Donor.donations).selectinload(Donation.project))
            .where(Donor.id == donor_id)
        )
        if donor is None:
            raise ValueError("Donor not found")

        allowed = accessible_project_ids()
        donations = list(donor.donations)
        if allowed is not None:
            donations = [d for d in donations if d.project_id in set(allowed)]
            if not donations and donor.donations:
                raise AccessDenied("You cannot view this donor.")

        by_project: dict[int, dict] = {}
        donation_rows = []
        for d in sorted(
            donations,
            key=lambda x: (x.donation_date, x.id),
            reverse=True,
        ):
            project_name = d.project.name if d.project else f"Project #{d.project_id}"
            donation_rows.append(
                {
                    "id": d.id,
                    "date": d.donation_date,
                    "project_id": d.project_id,
                    "project_name": project_name,
                    "pledged": _dec(d.pledged_amount),
                    "paid": _dec(d.paid_amount),
                    "remaining": d.remaining_amount,
                    "method": d.payment_method,
                    "status": d.status,
                    "reference": d.reference or "",
                    "notes": d.notes or "",
                }
            )
            bucket = by_project.setdefault(
                d.project_id,
                {
                    "project_id": d.project_id,
                    "project_name": project_name,
                    "pledged": Decimal("0"),
                    "paid": Decimal("0"),
                    "remaining": Decimal("0"),
                    "donations": 0,
                    "first_date": d.donation_date,
                    "last_date": d.donation_date,
                },
            )
            bucket["pledged"] += _dec(d.pledged_amount)
            bucket["paid"] += _dec(d.paid_amount)
            bucket["donations"] += 1
            if d.donation_date < bucket["first_date"]:
                bucket["first_date"] = d.donation_date
            if d.donation_date > bucket["last_date"]:
                bucket["last_date"] = d.donation_date

        for bucket in by_project.values():
            rem = bucket["pledged"] - bucket["paid"]
            bucket["remaining"] = rem if rem > 0 else Decimal("0")

        projects = sorted(by_project.values(), key=lambda x: x["project_name"])
        total_pledged = sum((b["pledged"] for b in projects), Decimal("0"))
        total_paid = sum((b["paid"] for b in projects), Decimal("0"))
        rem = total_pledged - total_paid
        return {
            "donor": donor,
            "projects": projects,
            "donations": donation_rows,
            "total_pledged": total_pledged,
            "total_paid": total_paid,
            "total_remaining": rem if rem > 0 else Decimal("0"),
            "project_count": len(projects),
            "donation_count": len(donation_rows),
        }


def find_donor_by_email_or_name(
    email: str = "", name: str = ""
) -> Donor | None:
    require_auth()
    with SessionLocal() as session:
        donor = None
        email = (email or "").strip()
        name = (name or "").strip()
        if email:
            donor = session.scalar(
                select(Donor).where(Donor.email.ilike(email))
            )
        if donor is None and name:
            donor = session.scalar(
                select(Donor).where(Donor.name.ilike(name))
            )
        if donor is None:
            return None
        session.expunge(donor)
        return donor


def find_or_create_donor(values: dict) -> tuple[int, bool]:
    require_auth()
    existing = find_donor_by_email_or_name(
        email=values.get("email", ""),
        name=values.get("name", ""),
    )
    if existing is not None:
        return existing.id, False
    return save_donor(None, values), True


def save_donor(donor_id: int | None, values: dict) -> int:
    require_auth()
    with SessionLocal.begin() as session:
        values = dict(values)
        values.pop("project_id", None)
        if donor_id is None:
            donor = Donor(**values)
            session.add(donor)
            session.flush()
            return donor.id
        donor = session.get(Donor, donor_id)
        if donor is None:
            raise ValueError("Donor not found")
        for key, value in values.items():
            setattr(donor, key, value)
        return donor.id


def delete_donor(donor_id: int) -> None:
    require_admin()
    with SessionLocal.begin() as session:
        donor = session.get(Donor, donor_id)
        if donor is not None:
            session.delete(donor)


# ---------- Donations ----------

def list_donations(project_id: int) -> list[Donation]:
    require_project_access(project_id)
    with SessionLocal() as session:
        donations = session.scalars(
            select(Donation)
            .options(
                selectinload(Donation.donor),
                selectinload(Donation.collected_by),
            )
            .where(Donation.project_id == project_id)
            .order_by(Donation.donation_date.desc(), Donation.id.desc())
        ).all()
        result = list(donations)
        session.expunge_all()
        return result


def list_donations_by_collector(
    collector_user_id: int,
    *,
    project_id: int | None = None,
) -> list[Donation]:
    """Donations collected by a staff user (scoped to accessible projects)."""
    require_auth()
    with SessionLocal() as session:
        query = (
            select(Donation)
            .options(
                selectinload(Donation.donor),
                selectinload(Donation.project),
                selectinload(Donation.collected_by),
            )
            .where(Donation.collected_by_user_id == collector_user_id)
            .order_by(Donation.donation_date.desc(), Donation.id.desc())
        )
        if project_id is not None:
            require_project_access(project_id)
            query = query.where(Donation.project_id == project_id)
        else:
            allowed = accessible_project_ids()
            if allowed is not None:
                if not allowed:
                    return []
                query = query.where(Donation.project_id.in_(allowed))
        result = list(session.scalars(query).all())
        session.expunge_all()
        return result


def _receiver_name(user: User | None = None) -> str:
    if user is not None:
        return user.display_name
    return (
        (current_session.full_name or "").strip()
        or (current_session.username or "").strip()
        or "Staff"
    )


def _resolve_collector(session, user_id: int | None) -> User | None:
    if user_id is None:
        return None
    return session.get(User, int(user_id))


def _add_payment(
    session,
    *,
    donation_id: int,
    amount: Decimal,
    payment_date,
    payment_method: str,
    reference: str = "",
    notes: str = "",
    received_by: str | None = None,
) -> None:
    if amount <= 0:
        return
    session.add(
        DonationPayment(
            donation_id=donation_id,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method or "Cash",
            received_by=received_by or _receiver_name(),
            reference=reference or "",
            notes=notes or "",
        )
    )


def save_donation(donation_id: int | None, values: dict) -> int:
    values = dict(values)
    project_id = values.get("project_id")
    if donation_id is None:
        require_project_access(project_id)
    else:
        require_auth()
        with SessionLocal() as session:
            existing = session.get(Donation, donation_id)
            if existing is None:
                raise ValueError("Donation not found")
            require_project_access(existing.project_id)
            if project_id is not None:
                require_project_access(int(project_id))

    with SessionLocal.begin() as session:
        pledged = _dec(values.get("pledged_amount", 0))
        paid = _dec(values.get("paid_amount", 0))
        if paid > pledged:
            raise ValueError("Paid amount cannot exceed pledged amount.")
        values["status"] = compute_donation_status(pledged, paid)
        values["pledged_amount"] = pledged
        values["paid_amount"] = paid
        collector_id = values.get("collected_by_user_id")
        if collector_id in ("", None):
            collector_id = current_session.user_id
        else:
            collector_id = int(collector_id)
        values["collected_by_user_id"] = collector_id
        collector = _resolve_collector(session, collector_id)
        if collector_id is not None and collector is None:
            raise ValueError("Collected-by user was not found.")
        receiver = _receiver_name(collector)
        pay_date = values.get("donation_date")
        method = values.get("payment_method") or "Cash"
        reference = values.get("reference") or ""
        notes = values.get("notes") or ""

        if donation_id is None:
            donation = Donation(**values)
            session.add(donation)
            session.flush()
            _add_payment(
                session,
                donation_id=donation.id,
                amount=paid,
                payment_date=pay_date,
                payment_method=method,
                reference=reference,
                notes=notes,
                received_by=receiver,
            )
            return donation.id

        donation = session.get(Donation, donation_id)
        if donation is None:
            raise ValueError("Donation not found")
        previous_paid = _dec(donation.paid_amount)
        for key, value in values.items():
            setattr(donation, key, value)
        donation.sync_status()
        delta = paid - previous_paid
        if delta > 0:
            _add_payment(
                session,
                donation_id=donation.id,
                amount=delta,
                payment_date=pay_date,
                payment_method=method,
                reference=reference,
                notes=notes,
                received_by=receiver,
            )
        return donation.id


def list_donor_payments(donor_id: int) -> list[dict]:
    """Payment installments for a donor (clickable paid-fund detail)."""
    require_auth()
    with SessionLocal() as session:
        donor = session.get(Donor, donor_id)
        if donor is None:
            raise ValueError("Donor not found")

        query = (
            select(DonationPayment)
            .join(Donation, DonationPayment.donation_id == Donation.id)
            .options(
                selectinload(DonationPayment.donation).selectinload(Donation.project),
                selectinload(DonationPayment.donation).selectinload(Donation.donor),
            )
            .where(Donation.donor_id == donor_id)
            .order_by(DonationPayment.payment_date.desc(), DonationPayment.id.desc())
        )
        allowed = accessible_project_ids()
        if allowed is not None:
            if not allowed:
                return []
            query = query.where(Donation.project_id.in_(allowed))

        rows = []
        for payment in session.scalars(query).all():
            donation = payment.donation
            project_name = (
                donation.project.name
                if donation and donation.project
                else f"Project #{donation.project_id if donation else '?'}"
            )
            rows.append(
                {
                    "id": payment.id,
                    "donation_id": payment.donation_id,
                    "amount": _dec(payment.amount),
                    "date": payment.payment_date,
                    "method": payment.payment_method or "Cash",
                    "received_by": payment.received_by or "",
                    "reference": payment.reference or "",
                    "notes": payment.notes or "",
                    "project_id": donation.project_id if donation else None,
                    "project_name": project_name,
                    "pledged": _dec(donation.pledged_amount) if donation else Decimal("0"),
                    "donation_paid": _dec(donation.paid_amount) if donation else Decimal("0"),
                    "status": donation.status if donation else "",
                }
            )
        return rows


def list_donation_payments(donation_id: int) -> list[dict]:
    require_auth()
    with SessionLocal() as session:
        donation = session.get(Donation, donation_id)
        if donation is None:
            raise ValueError("Donation not found")
        require_project_access(donation.project_id)
        payments = session.scalars(
            select(DonationPayment)
            .where(DonationPayment.donation_id == donation_id)
            .order_by(DonationPayment.payment_date.desc(), DonationPayment.id.desc())
        ).all()
        return [
            {
                "id": p.id,
                "donation_id": p.donation_id,
                "amount": _dec(p.amount),
                "date": p.payment_date,
                "method": p.payment_method or "Cash",
                "received_by": p.received_by or "",
                "reference": p.reference or "",
                "notes": p.notes or "",
            }
            for p in payments
        ]


def delete_donation(donation_id: int) -> None:
    require_auth()
    with SessionLocal.begin() as session:
        donation = session.get(Donation, donation_id)
        if donation is None:
            return
        require_project_access(donation.project_id)
        session.delete(donation)


# ---------- Expenses ----------

def list_expenses(project_id: int) -> list[Expense]:
    require_project_access(project_id)
    with SessionLocal() as session:
        expenses = session.scalars(
            select(Expense)
            .where(Expense.project_id == project_id)
            .order_by(Expense.expense_date.desc(), Expense.id.desc())
        ).all()
        result = list(expenses)
        for expense in result:
            session.expunge(expense)
        return result


def save_expense(expense_id: int | None, values: dict) -> int:
    values = dict(values)
    if expense_id is None:
        require_project_access(values.get("project_id"))
    with SessionLocal.begin() as session:
        if expense_id is None:
            expense = Expense(**values)
            session.add(expense)
            session.flush()
            return expense.id
        expense = session.get(Expense, expense_id)
        if expense is None:
            raise ValueError("Expense not found")
        require_project_access(expense.project_id)
        for key, value in values.items():
            setattr(expense, key, value)
        return expense.id


def delete_expense(expense_id: int) -> None:
    require_auth()
    with SessionLocal.begin() as session:
        expense = session.get(Expense, expense_id)
        if expense is None:
            return
        require_project_access(expense.project_id)
        session.delete(expense)


# ---------- Reports / aggregates ----------

def project_report_stats(project_id: int) -> dict:
    require_project_access(project_id)
    with SessionLocal() as session:
        project = session.scalar(select(Project).where(Project.id == project_id))
        if project is None:
            raise ValueError("Project not found")
        _attach_project_aggregates(session, [project])

        by_method = {
            row[0] or "Other": _dec(row[1])
            for row in session.execute(
                select(
                    Donation.payment_method,
                    func.coalesce(func.sum(Donation.paid_amount), 0),
                )
                .where(Donation.project_id == project_id)
                .group_by(Donation.payment_method)
            )
        }
        by_status = {
            row[0] or "Pending": int(row[1])
            for row in session.execute(
                select(Donation.status, func.count())
                .where(Donation.project_id == project_id)
                .group_by(Donation.status)
            )
        }
        monthly = {
            row[0]: _dec(row[1])
            for row in session.execute(
                select(
                    func.strftime("%Y-%m", Donation.donation_date),
                    func.coalesce(func.sum(Donation.paid_amount), 0),
                )
                .where(Donation.project_id == project_id)
                .group_by(func.strftime("%Y-%m", Donation.donation_date))
                .order_by(func.strftime("%Y-%m", Donation.donation_date))
            )
        }
        by_category = {
            row[0] or "Other": _dec(row[1])
            for row in session.execute(
                select(
                    Expense.category,
                    func.coalesce(func.sum(Expense.amount), 0),
                )
                .where(Expense.project_id == project_id)
                .group_by(Expense.category)
            )
        }

        session.expunge(project)
        return {
            "project": project,
            "by_method": by_method,
            "by_status": by_status,
            "monthly": monthly,
            "by_category": by_category,
            "donor_count": project.unique_donor_count,
            "donation_count": project.donation_count,
            "expense_count": int(
                session.scalar(
                    select(func.count())
                    .select_from(Expense)
                    .where(Expense.project_id == project_id)
                )
                or 0
            ),
        }


def portfolio_report_stats(*, top_n: int = 12) -> dict:
    """Overall multi-project report (admin / accessible portfolio)."""
    require_auth()
    projects = list_projects(enforce_acl=True)
    projects_sorted = sorted(
        projects, key=lambda p: p.amount_raised, reverse=True
    )

    total_raised = sum((p.amount_raised for p in projects), Decimal("0"))
    total_pledged = sum((p.amount_pledged for p in projects), Decimal("0"))
    total_expenses = sum((p.total_expenses for p in projects), Decimal("0"))
    total_target = sum((_dec(p.target_amount) for p in projects), Decimal("0"))
    outstanding = total_pledged - total_raised
    if outstanding < 0:
        outstanding = Decimal("0")

    def _chart_label(project: Project) -> str:
        # Prefer theme before em-dash, keep id so bars stay distinguishable.
        base = project.name.split("—")[0].strip() if "—" in project.name else project.name
        if len(base) > 24:
            base = base[:22] + "…"
        return f"#{project.id} {base}"

    # Chart series: top N by raised, remainder rolled into "Other".
    top = projects_sorted[: max(1, top_n)]
    other = projects_sorted[max(1, top_n) :]
    by_project = []
    for p in top:
        by_project.append(
            {
                "id": p.id,
                "name": _chart_label(p),
                "full_name": p.name,
                "raised": p.amount_raised,
                "pledged": p.amount_pledged,
                "expenses": p.total_expenses,
                "outstanding": max(
                    Decimal("0"), p.amount_pledged - p.amount_raised
                ),
                "target": _dec(p.target_amount),
            }
        )
    if other:
        by_project.append(
            {
                "id": None,
                "name": f"Other ({len(other)})",
                "full_name": f"{len(other)} more projects",
                "raised": sum((p.amount_raised for p in other), Decimal("0")),
                "pledged": sum((p.amount_pledged for p in other), Decimal("0")),
                "expenses": sum((p.total_expenses for p in other), Decimal("0")),
                "outstanding": sum(
                    (
                        max(Decimal("0"), p.amount_pledged - p.amount_raised)
                        for p in other
                    ),
                    Decimal("0"),
                ),
                "target": sum((_dec(p.target_amount) for p in other), Decimal("0")),
            }
        )

    top_ids = [p.id for p in top]
    monthly_by_project: dict[str, dict[str, Decimal]] = {}
    months: list[str] = []
    with SessionLocal() as session:
        if top_ids:
            rows = session.execute(
                select(
                    func.strftime("%Y-%m", Donation.donation_date),
                    Donation.project_id,
                    func.coalesce(func.sum(Donation.paid_amount), 0),
                )
                .where(Donation.project_id.in_(top_ids))
                .group_by(
                    func.strftime("%Y-%m", Donation.donation_date),
                    Donation.project_id,
                )
                .order_by(func.strftime("%Y-%m", Donation.donation_date))
            ).all()
            id_to_name = {p.id: _chart_label(p) for p in top}
            month_set: list[str] = []
            for month, pid, amount in rows:
                if month not in month_set:
                    month_set.append(month)
                label = id_to_name.get(pid, f"#{pid}")
                monthly_by_project.setdefault(label, {})
                monthly_by_project[label][month] = _dec(amount)
            months = month_set

        donor_count = (
            session.scalar(select(func.count(distinct(Donation.donor_id)))) or 0
            if current_session.is_admin
            else (
                session.scalar(
                    select(func.count(distinct(Donation.donor_id))).where(
                        Donation.project_id.in_(
                            current_session.project_ids or [-1]
                        )
                    )
                )
                or 0
            )
        )

    return {
        "project_count": len(projects),
        "donor_count": int(donor_count),
        "donation_count": sum(p.donation_count for p in projects),
        "total_target": total_target,
        "total_raised": total_raised,
        "total_pledged": total_pledged,
        "total_outstanding": outstanding,
        "total_expenses": total_expenses,
        "by_project": by_project,
        "monthly_by_project": monthly_by_project,
        "months": months,
    }


def global_dashboard_stats(
    user: User | None = None,
    *,
    role: str | None = None,
    project_ids: list[int] | None = None,
) -> dict:
    require_auth()
    projects = list_projects(
        user,
        role=role,
        project_ids=project_ids,
        include_archived=False,
        enforce_acl=True,
    )
    total_raised = sum((p.amount_raised for p in projects), Decimal("0"))
    total_pledged = sum((p.amount_pledged for p in projects), Decimal("0"))
    total_outstanding = total_pledged - total_raised
    if total_outstanding < 0:
        total_outstanding = Decimal("0")
    total_target = sum((_dec(p.target_amount) for p in projects), Decimal("0"))
    total_expenses = sum((p.total_expenses for p in projects), Decimal("0"))
    donation_count = sum(p.donation_count for p in projects)

    with SessionLocal() as session:
        allowed = accessible_project_ids()
        if allowed is None:
            donor_count = session.scalar(select(func.count()).select_from(Donor)) or 0
        elif not allowed:
            donor_count = 0
        else:
            donor_count = (
                session.scalar(
                    select(func.count(distinct(Donation.donor_id))).where(
                        Donation.project_id.in_(allowed)
                    )
                )
                or 0
            )

    return {
        "projects": projects,
        "project_count": len(projects),
        "active_count": sum(1 for p in projects if p.status == "Active"),
        "donor_count": int(donor_count),
        "donation_count": donation_count,
        "total_raised": total_raised,
        "total_pledged": total_pledged,
        "total_outstanding": total_outstanding,
        "total_target": total_target,
        "total_expenses": total_expenses,
    }
