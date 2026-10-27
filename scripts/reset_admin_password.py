"""
Offline emergency admin password reset (developer / support only).

Preferred for customers: open the app → Sign in → "Forgot admin password?"
and use the recovery key held by MayleSoft support.

This script bypasses the recovery key. It is intentionally awkward to run and
is NOT included in the Windows customer build.

Usage (from the project folder, with venv active):

    python scripts/reset_admin_password.py --confirm-offline-reset
    python scripts/reset_admin_password.py --confirm-offline-reset --password MyNewPass123
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
    parser = argparse.ArgumentParser(description="Emergency offline admin password reset")
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
    parser.add_argument(
        "--confirm-offline-reset",
        action="store_true",
        help="Required. Confirms you are a trusted operator with project access.",
    )
    args = parser.parse_args()

    if not args.confirm_offline_reset:
        print(
            "Refusing to reset without --confirm-offline-reset.\n"
            "Customers should use Sign in → Forgot admin password? with a recovery key.\n"
            "Support/developers only: add --confirm-offline-reset."
        )
        return 2

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
