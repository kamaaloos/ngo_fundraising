from __future__ import annotations

import os
from pathlib import Path

import pytest

# Demo seed is off by default; keep explicit skips for older helpers.
os.environ.setdefault("NGO_SKIP_DEMO_SEED", "1")
os.environ.pop("NGO_SEED_DEMO", None)


@pytest.fixture()
def db_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("NGO_SKIP_DEMO_SEED", "1")
    monkeypatch.delenv("NGO_SEED_DEMO", raising=False)
    db_path = tmp_path / "test.sqlite3"

    from app.auth.session import current_session
    from app.db import database

    database.configure_engine(db_path)
    database.init_db()
    current_session.clear()
    yield database
    current_session.clear()
    database.engine.dispose()


@pytest.fixture()
def admin_session(db_env):
    from app.auth.session import current_session
    from app.db.repository import authenticate
    from app.db.seed import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME

    user = authenticate(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
    assert user is not None
    current_session.user_id = user.id
    current_session.username = user.username
    current_session.full_name = user.full_name or user.username
    current_session.role = user.role
    current_session.project_ids = []
    current_session.current_project_id = None
    return user
