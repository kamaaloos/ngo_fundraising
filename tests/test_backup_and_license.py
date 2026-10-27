from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import select

from app.db.database import (
    DATABASE_PATH,
    SessionLocal,
    export_database_backup,
    get_app_meta,
    restore_database_backup,
    set_app_meta,
)
from app.db.models import Donor
from app.licensing import (
    LICENSE_EXPIRES_KEY,
    LICENSE_TOKEN_KEY,
    apply_license_code,
    build_license_code,
    get_license_status,
)
from app.support_identity import ensure_install_id, get_install_id


def test_export_and_restore_roundtrip(admin_session, tmp_path: Path):
    with SessionLocal.begin() as session:
        session.add(Donor(name="Backup Probe", email="probe@example.org"))

    backup = tmp_path / "copy.sqlite3"
    export_database_backup(backup)
    assert backup.exists()
    assert backup.stat().st_size > 0

    with SessionLocal.begin() as session:
        session.add(Donor(name="After Export", email="after@example.org"))

    restore_database_backup(backup)

    with SessionLocal() as session:
        names = {d.name for d in session.scalars(select(Donor)).all()}
    assert "Backup Probe" in names
    assert "After Export" not in names
    assert DATABASE_PATH.exists()


def test_license_rejects_expiry_without_token(admin_session):
    ensure_install_id()
    install_id = get_install_id()
    expires = date.today() + timedelta(days=400)
    code = build_license_code(install_id, expires)
    apply_license_code(code)
    assert get_license_status().valid is True

    # Raw expiry edit without matching token must fail closed.
    set_app_meta(LICENSE_EXPIRES_KEY, (date.today() + timedelta(days=900)).isoformat())
    assert get_license_status().valid is False

    # Missing token entirely must fail closed.
    set_app_meta(LICENSE_TOKEN_KEY, "")
    set_app_meta(LICENSE_EXPIRES_KEY, expires.isoformat())
    assert get_license_status().valid is False
    assert get_app_meta(LICENSE_EXPIRES_KEY) == expires.isoformat()
