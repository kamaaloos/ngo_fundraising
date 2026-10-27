from decimal import Decimal

import pytest

from app.db.models import compute_donation_status
from app.db.seed import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME


def test_compute_donation_status_pending_remaining_completed():
    assert compute_donation_status(100, 0) == "Pending"
    assert compute_donation_status(Decimal("100"), Decimal("40")) == "Remaining"
    assert compute_donation_status(100, 100) == "Completed"
    assert compute_donation_status(50, 80) == "Completed"


def test_authenticate_default_admin(db_env):
    from app.db.repository import authenticate

    assert authenticate(DEFAULT_ADMIN_USERNAME, "wrong") is None
    user = authenticate(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    assert user is not None
    assert user.role == "admin"
    assert bool(user.must_change_password)


def test_change_password_clears_flag(admin_session):
    from app.db.repository import authenticate, change_own_password

    change_own_password(admin_session.id, DEFAULT_ADMIN_PASSWORD, "new-secret-99")
    assert authenticate(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD) is None
    user = authenticate(DEFAULT_ADMIN_USERNAME, "new-secret-99")
    assert user is not None
    assert not user.must_change_password
