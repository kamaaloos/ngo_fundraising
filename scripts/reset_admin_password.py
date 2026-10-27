"""
Reset the admin login password (local SQLite app).

Preferred for customers: open the app → Sign in → "Forgot admin password?"

Developer / support usage (from the project folder, with venv active):

    python scripts/reset_admin_password.py
    python scripts/reset_admin_password.py --password MyNewPass123

Default temporary password is admin123; you will be forced to change it at login.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as: python scripts/reset_admin_password.py
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import init_db
from app.db.repository import reset_local_admin_password
from app.db.seed import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset NGO Fund admin password")
    parser.add_argument(
        "--password",
        default=DEFAULT_ADMIN_PASSWORD,
        help=f"Temporary password (default: {DEFAULT_ADMIN_PASSWORD})",
    )
    parser.add_argument(
        "--username",
        default=DEFAULT_ADMIN_USERNAME,
        help=f"Account to reset (default: {DEFAULT_ADMIN_USERNAME})",
    )
    args = parser.parse_args()

    init_db()
    try:
        # Support/installer path: trusted operator with project access.
        username, temp = reset_local_admin_password(
            temporary_password=args.password,
            username=args.username,
            allow_unauthenticated_script=True,
        )
    except ValueError as exc:
        print(exc)
        return 1

    print(f"Password reset for '{username}'.")
    print(f"Temporary password: {temp}")
    print("Sign in, then set a new password when prompted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
