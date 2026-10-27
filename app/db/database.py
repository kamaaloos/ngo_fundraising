from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

APP_DIR = Path.home() / "AppData" / "Local" / "NGOFundraisingManager"
APP_DIR.mkdir(parents=True, exist_ok=True)

# Bump when adding additive migrations in MIGRATIONS below.
SCHEMA_VERSION = 6

Base = declarative_base()

engine = None  # type: ignore[assignment]
SessionLocal = sessionmaker(autoflush=False, expire_on_commit=False)
DATABASE_PATH: Path
DATABASE_URL: str


def _resolve_database_path() -> Path:
    env_db = os.environ.get("NGO_DB_PATH", "").strip()
    path = Path(env_db) if env_db else APP_DIR / "fundraising.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def configure_engine(path: Path | None = None):
    """(Re)bind the global engine — used by the app and by tests."""
    global engine, DATABASE_PATH, DATABASE_URL, SessionLocal
    if engine is not None:
        engine.dispose()
    DATABASE_PATH = path or _resolve_database_path()
    DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SessionLocal.configure(bind=engine)


configure_engine()


# Additive, non-destructive steps keyed by target version.
MIGRATIONS: dict[int, list[str]] = {
    4: [
        "ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0",
        "UPDATE users SET must_change_password = 1 WHERE username = 'admin'",
    ],
    5: [
        """
        CREATE TABLE IF NOT EXISTS donation_payments (
            id INTEGER NOT NULL PRIMARY KEY,
            donation_id INTEGER NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            payment_date DATE NOT NULL,
            payment_method VARCHAR(50) DEFAULT 'Cash',
            received_by VARCHAR(150) DEFAULT '',
            reference VARCHAR(100) DEFAULT '',
            notes TEXT DEFAULT '',
            created_at DATETIME NOT NULL,
            FOREIGN KEY(donation_id) REFERENCES donations (id) ON DELETE CASCADE
        )
        """,
        """
        INSERT INTO donation_payments (
            donation_id, amount, payment_date, payment_method,
            received_by, reference, notes, created_at
        )
        SELECT
            d.id,
            d.paid_amount,
            d.donation_date,
            COALESCE(d.payment_method, 'Cash'),
            'System migration',
            COALESCE(d.reference, ''),
            COALESCE(d.notes, ''),
            CURRENT_TIMESTAMP
        FROM donations d
        WHERE d.paid_amount > 0
          AND NOT EXISTS (
              SELECT 1 FROM donation_payments p WHERE p.donation_id = d.id
          )
        """,
    ],
    6: [
        "ALTER TABLE donations ADD COLUMN collected_by_user_id INTEGER "
        "REFERENCES users(id) ON DELETE SET NULL",
    ],
}


def _ensure_meta_table(connection) -> int:
    connection.execute(
        text(
            "CREATE TABLE IF NOT EXISTS app_meta ("
            "key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
    )
    row = connection.execute(
        text("SELECT value FROM app_meta WHERE key = 'schema_version'")
    ).fetchone()
    return int(row[0]) if row else 0


def _set_schema_version(connection, version: int) -> None:
    connection.execute(
        text(
            "INSERT INTO app_meta(key, value) VALUES('schema_version', :v) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value"
        ),
        {"v": str(version)},
    )


def get_app_meta(key: str) -> str | None:
    with engine.begin() as connection:
        _ensure_meta_table(connection)
        row = connection.execute(
            text("SELECT value FROM app_meta WHERE key = :k"),
            {"k": key},
        ).fetchone()
        return str(row[0]) if row else None


def set_app_meta(key: str, value: str) -> None:
    with engine.begin() as connection:
        _ensure_meta_table(connection)
        connection.execute(
            text(
                "INSERT INTO app_meta(key, value) VALUES(:k, :v) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value"
            ),
            {"k": key, "v": value},
        )


def _column_exists(connection, table: str, column: str) -> bool:
    rows = connection.execute(text(f'PRAGMA table_info("{table}")')).fetchall()
    return any(row[1] == column for row in rows)


def backup_database() -> Path | None:
    """Copy the live SQLite file before applying migrations (safe during init)."""
    if not DATABASE_PATH.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = DATABASE_PATH.parent / f"fundraising_backup_{stamp}.sqlite3"
    shutil.copy2(DATABASE_PATH, dest)
    return dest


def export_database_backup(dest: Path | str) -> Path:
    """Write a consistent snapshot of the live database to ``dest`` (Settings UI)."""
    import sqlite3

    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.resolve() == DATABASE_PATH.resolve():
        raise ValueError("Backup destination cannot be the live database file.")

    # Checkpoint + online backup so WAL pages are included.
    if engine is not None:
        with engine.connect() as conn:
            conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
            conn.commit()
        engine.dispose()
    try:
        with sqlite3.connect(DATABASE_PATH.as_posix()) as src:
            with sqlite3.connect(dest_path.as_posix()) as dst:
                src.backup(dst)
    finally:
        configure_engine(DATABASE_PATH)
    return dest_path


def restore_database_backup(source: Path | str) -> Path:
    """Replace the live database with ``source``. Caller should restart the app."""
    import sqlite3

    src_path = Path(source)
    if not src_path.exists():
        raise FileNotFoundError(f"Backup not found: {src_path}")
    if src_path.resolve() == DATABASE_PATH.resolve():
        raise ValueError("Cannot restore from the live database path.")

    # Validate it looks like a SQLite database before replacing anything.
    try:
        with sqlite3.connect(src_path.as_posix()) as conn:
            row = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone()
            if row is None:
                raise ValueError("File is not a valid NGO Fundraising backup.")
    except sqlite3.Error as exc:
        raise ValueError(f"Invalid SQLite backup: {exc}") from exc

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety = DATABASE_PATH.parent / f"fundraising_pre_restore_{stamp}.sqlite3"
    if DATABASE_PATH.exists():
        shutil.copy2(DATABASE_PATH, safety)

    if engine is not None:
        engine.dispose()

    # Clear WAL sidecars so the restored file is the sole source of truth.
    for suffix in ("-wal", "-shm"):
        side = Path(str(DATABASE_PATH) + suffix)
        if side.exists():
            side.unlink()

    shutil.copy2(src_path, DATABASE_PATH)
    configure_engine(DATABASE_PATH)
    return safety


def _run_migrations(connection, current: int, target: int) -> None:
    for version in range(current + 1, target + 1):
        for sql in MIGRATIONS.get(version, []):
            if "ADD COLUMN" in sql.upper():
                parts = sql.split()
                try:
                    table = parts[2]
                    col = parts[parts.index("COLUMN") + 1]
                except (ValueError, IndexError):
                    table, col = "", ""
                if table and col and _column_exists(connection, table, col):
                    continue
            connection.execute(text(sql))


def init_db():
    import app.db.models  # noqa: F401

    with engine.begin() as connection:
        inspector = inspect(connection)
        had_users = "users" in set(inspector.get_table_names())
        current_before = _ensure_meta_table(connection)

    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        current = _ensure_meta_table(connection)
        if not had_users and current_before == 0:
            # Fresh install — model already has latest columns.
            _set_schema_version(connection, SCHEMA_VERSION)
        elif current < SCHEMA_VERSION:
            backup_database()
            # Legacy unmarked DBs (version 0 with tables) start at v3 baseline.
            from_version = current if current > 0 else 3
            _run_migrations(connection, from_version, SCHEMA_VERSION)
            _set_schema_version(connection, SCHEMA_VERSION)
        else:
            _set_schema_version(connection, SCHEMA_VERSION)

    from app.db.seed import seed_defaults

    seed_defaults()
