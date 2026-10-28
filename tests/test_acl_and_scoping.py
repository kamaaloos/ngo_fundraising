from decimal import Decimal

import pytest

from app.auth.passwords import hash_password
from app.auth.session import current_session
from app.db.access import AccessDenied
from app.db.database import SessionLocal
from app.db.models import Donation, Donor, Project, User
from app.db.repository import (
    find_donor_by_email_or_name,
    find_or_create_donor,
    get_project,
    global_dashboard_stats,
    list_all_donors,
    list_donors,
    list_projects,
    save_donation,
    save_donor,
    save_project,
)
from app.io.importers import (
    import_donors_from_file,
    import_donors_linked_to_project,
    import_projects_from_file,
)


def _make_user_project_fixture(admin_session):
    """Admin creates two projects; a limited user is assigned to only one."""
    p1 = save_project(None, {"name": "Alpha", "target_amount": Decimal("1000"), "status": "Active"})
    p2 = save_project(None, {"name": "Beta", "target_amount": Decimal("2000"), "status": "Active"})

    with SessionLocal.begin() as session:
        donor = Donor(name="Pat Donor", email="pat@example.org")
        session.add(donor)
        session.flush()
        session.add_all(
            [
                Donation(
                    donor_id=donor.id,
                    project_id=p1,
                    pledged_amount=Decimal("100"),
                    paid_amount=Decimal("100"),
                    status="Completed",
                ),
                Donation(
                    donor_id=donor.id,
                    project_id=p2,
                    pledged_amount=Decimal("50"),
                    paid_amount=Decimal("0"),
                    status="Pending",
                ),
            ]
        )
        limited = User(
            username="worker",
            password_hash=hash_password("workerpass1"),
            full_name="Worker",
            role="user",
            is_active=True,
            must_change_password=False,
        )
        session.add(limited)
        session.flush()
        project = session.get(Project, p1)
        limited.projects = [project]
        session.flush()
        limited_id = limited.id

    return p1, p2, limited_id


def test_project_scoping_for_non_admin(admin_session):
    p1, p2, limited_id = _make_user_project_fixture(admin_session)

    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [p1]

    projects = list_projects()
    assert {p.id for p in projects} == {p1}

    assert get_project(p1) is not None
    with pytest.raises(AccessDenied):
        get_project(p2)


def test_non_admin_cannot_create_project(admin_session):
    p1, _p2, limited_id = _make_user_project_fixture(admin_session)
    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [p1]

    with pytest.raises(AccessDenied):
        save_project(None, {"name": "Nope", "target_amount": Decimal("1"), "status": "Active"})


def test_donor_list_scoped_and_dashboard_counts(admin_session):
    p1, p2, limited_id = _make_user_project_fixture(admin_session)

    # Admin sees both donors / all projects stats.
    donors, total = list_donors(page=1, page_size=50)
    assert total >= 1

    stats = global_dashboard_stats()
    assert stats["project_count"] >= 2
    assert stats["donation_count"] >= 2

    # Limited user: only project p1 donors when filtered; dashboard scoped.
    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [p1]

    donors, total = list_donors(project_id=p1, page=1, page_size=50)
    assert total == 1
    assert donors[0].name == "Pat Donor"

    with pytest.raises(AccessDenied):
        list_donors(project_id=p2)

    stats = global_dashboard_stats()
    assert stats["project_count"] == 1
    assert stats["donation_count"] == 1
    assert stats["donor_count"] == 1


def test_list_all_donors_scoped_for_non_admin(admin_session):
    p1, p2, limited_id = _make_user_project_fixture(admin_session)
    other = save_donor(None, {"name": "Only Beta Donor", "email": "beta@example.org"})
    save_donation(
        None,
        {
            "donor_id": other,
            "project_id": p2,
            "pledged_amount": Decimal("25"),
            "paid_amount": Decimal("25"),
            "payment_method": "Cash",
        },
    )
    unused = save_donor(None, {"name": "Unused Donor", "email": "new@example.org"})

    admin_names = {d.name for d in list_all_donors()}
    assert "Pat Donor" in admin_names
    assert "Only Beta Donor" in admin_names
    assert "Unused Donor" in admin_names

    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [p1]

    scoped = {d.name for d in list_all_donors()}
    assert "Pat Donor" in scoped
    assert "Unused Donor" in scoped
    assert "Only Beta Donor" not in scoped
    assert unused in {d.id for d in list_all_donors()}


def test_sql_aggregates_on_project(admin_session):
    p1, _p2, _ = _make_user_project_fixture(admin_session)
    project = get_project(p1)
    assert project is not None
    assert project.amount_raised == Decimal("100.00")
    assert project.amount_pledged == Decimal("100.00")
    assert project.donation_count == 1
    assert project.unique_donor_count == 1


def test_save_donation_requires_project_access(admin_session):
    p1, p2, limited_id = _make_user_project_fixture(admin_session)
    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [p1]

    from sqlalchemy import select

    with SessionLocal() as session:
        donor_id = session.scalar(select(Donor.id))

    save_donation(
        None,
        {
            "donor_id": donor_id,
            "project_id": p1,
            "pledged_amount": Decimal("10"),
            "paid_amount": Decimal("10"),
            "payment_method": "Cash",
        },
    )
    with pytest.raises(AccessDenied):
        save_donation(
            None,
            {
                "donor_id": donor_id,
                "project_id": p2,
                "pledged_amount": Decimal("10"),
                "paid_amount": Decimal("0"),
                "payment_method": "Cash",
            },
        )


def test_save_donor_update_scoped(admin_session):
    p1, p2, limited_id = _make_user_project_fixture(admin_session)
    beta_only = save_donor(None, {"name": "Beta Only", "email": "beta-only@ex.org"})
    save_donation(
        None,
        {
            "donor_id": beta_only,
            "project_id": p2,
            "pledged_amount": Decimal("10"),
            "paid_amount": Decimal("10"),
            "payment_method": "Cash",
        },
    )

    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [p1]

    with pytest.raises(AccessDenied):
        save_donor(beta_only, {"name": "Hacked", "email": "beta-only@ex.org"})

    # Can still create a new donor.
    new_id = save_donor(None, {"name": "Worker New", "email": "worker-new@ex.org"})
    assert new_id > 0


def test_find_donor_scoped_and_conflict(admin_session):
    _p1, p2, limited_id = _make_user_project_fixture(admin_session)
    beta_only = save_donor(None, {"name": "Secret Beta", "email": "secret-beta@ex.org"})
    save_donation(
        None,
        {
            "donor_id": beta_only,
            "project_id": p2,
            "pledged_amount": Decimal("5"),
            "paid_amount": Decimal("5"),
            "payment_method": "Cash",
        },
    )

    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [_p1]

    assert find_donor_by_email_or_name(email="secret-beta@ex.org") is None
    assert (
        find_donor_by_email_or_name(
            email="secret-beta@ex.org", scoped=False
        ).id
        == beta_only
    )

    with pytest.raises(AccessDenied):
        find_or_create_donor(
            {"name": "Secret Beta", "email": "secret-beta@ex.org"}
        )

    reused_id, created = find_or_create_donor(
        {"name": "Secret Beta", "email": "secret-beta@ex.org"},
        allow_cross_project=True,
    )
    assert not created
    assert reused_id == beta_only


def test_import_acl_gates(admin_session, tmp_path):
    p1, p2, limited_id = _make_user_project_fixture(admin_session)
    donors_csv = tmp_path / "donors.csv"
    donors_csv.write_text("name,email\nAda,ada@ex.org\n", encoding="utf-8")
    projects_csv = tmp_path / "projects.csv"
    projects_csv.write_text(
        "name,target,status\nGamma,100,Active\n", encoding="utf-8"
    )

    current_session.user_id = limited_id
    current_session.username = "worker"
    current_session.role = "user"
    current_session.project_ids = [p1]

    with pytest.raises(AccessDenied):
        import_donors_from_file(donors_csv)
    with pytest.raises(AccessDenied):
        import_projects_from_file(projects_csv)
    with pytest.raises(AccessDenied):
        import_donors_linked_to_project(donors_csv, p2)

    # Assigned project: link import allowed.
    created, reused, donations, warnings = import_donors_linked_to_project(
        donors_csv, p1
    )
    assert created == 1
    assert donations == 1
    assert not warnings
