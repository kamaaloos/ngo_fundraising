"""Local app license / usage timer (support-managed extensions)."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from app.db.database import get_app_meta, set_app_meta
from app.support_identity import SUPPORT_CONTACT, ensure_install_id, get_install_id

# Shared with scripts/customer_registry.py — light protection, not hard DRM.
_LICENSE_SECRET = b"MayleSoft.NGOFundraising.License.v1.2026"

LICENSE_EXPIRES_KEY = "license_expires_on"
LICENSE_TOKEN_KEY = "license_token"
LICENSE_LAST_SEEN_KEY = "license_last_seen"
DEFAULT_TRIAL_DAYS = 30
WARN_WITHIN_DAYS = 14


@dataclass
class LicenseStatus:
    install_id: str
    expires_on: date | None
    days_remaining: int | None
    valid: bool
    is_trial: bool
    message: str


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _sign(install_id: str, expires_on: date) -> str:
    msg = f"{install_id.strip().upper()}|{expires_on.isoformat()}".encode("utf-8")
    digest = hmac.new(_LICENSE_SECRET, msg, hashlib.sha256).hexdigest()
    return digest[:20].upper()


def build_license_code(install_id: str, expires_on: date) -> str:
    """Developer-issued activation / extension code."""
    iid = install_id.strip().upper()
    sig = _sign(iid, expires_on)
    return f"MSL1-{iid}-{expires_on.isoformat()}-{sig}"


def parse_license_code(code: str) -> tuple[str, date, str]:
    raw = (code or "").strip().upper().replace(" ", "")
    parts = raw.split("-")
    # MSL1-NGO-XXXXXXXXXX-YYYY-MM-DD-SIGNATURE
    if len(parts) < 6 or parts[0] != "MSL1":
        raise ValueError(
            "Invalid license code format. Ask MayleSoft support for a valid code."
        )
    # install id may contain hyphens: NGO-XXXXXXXXXX
    # Pattern: MSL1 | NGO | HEX | YYYY | MM | DD | SIG
    if parts[1] != "NGO" or len(parts) < 7:
        raise ValueError("Invalid license code (install id).")
    install_id = f"{parts[1]}-{parts[2]}"
    try:
        expires_on = date(int(parts[3]), int(parts[4]), int(parts[5]))
    except ValueError as exc:
        raise ValueError("Invalid license expiry date in code.") from exc
    signature = parts[6]
    expected = _sign(install_id, expires_on)
    if not hmac.compare_digest(signature, expected):
        raise ValueError("License code signature is invalid.")
    return install_id, expires_on, signature


def _read_expires() -> date | None:
    raw = get_app_meta(LICENSE_EXPIRES_KEY)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw.strip())
    except ValueError:
        return None


def _anti_clock_rollback(today: date) -> None:
    """If the PC clock is moved backwards, keep the last seen day forward-only."""
    last = get_app_meta(LICENSE_LAST_SEEN_KEY)
    if last:
        try:
            last_seen = date.fromisoformat(last)
            if today < last_seen:
                # Treat rolled-back clock as still "at" last seen for checks.
                return
        except ValueError:
            pass
    set_app_meta(LICENSE_LAST_SEEN_KEY, today.isoformat())


def effective_today() -> date:
    today = _today()
    last = get_app_meta(LICENSE_LAST_SEEN_KEY)
    if last:
        try:
            last_seen = date.fromisoformat(last)
            if today < last_seen:
                return last_seen
        except ValueError:
            pass
    _anti_clock_rollback(today)
    return today


def ensure_trial_license(*, days: int = DEFAULT_TRIAL_DAYS) -> LicenseStatus:
    """Create a signed trial if this install has no license yet."""
    ensure_install_id()
    if _read_expires() is None:
        expires = _today() + timedelta(days=max(1, days))
        code = build_license_code(get_install_id(), expires)
        apply_license_code(code, allow_other_install=False)
    return get_license_status()


def apply_license_code(code: str, *, allow_other_install: bool = False) -> LicenseStatus:
    install_id, expires_on, _sig = parse_license_code(code)
    local_id = get_install_id()
    if not allow_other_install and install_id != local_id:
        raise ValueError(
            f"This code is for Install ID {install_id}, "
            f"but this computer is {local_id}."
        )
    current = _read_expires()
    if current is not None and expires_on < current:
        raise ValueError(
            f"This code expires on {expires_on.isoformat()}, "
            f"which is earlier than the current license ({current.isoformat()})."
        )
    set_app_meta(LICENSE_EXPIRES_KEY, expires_on.isoformat())
    set_app_meta(LICENSE_TOKEN_KEY, code.strip().upper())
    set_app_meta(LICENSE_LAST_SEEN_KEY, effective_today().isoformat())
    return get_license_status()


def get_license_status() -> LicenseStatus:
    install_id = get_install_id()
    expires = _read_expires()
    today = effective_today()
    token = get_app_meta(LICENSE_TOKEN_KEY) or ""
    is_trial = "TRIAL" in token.upper()  # not used; infer from short span optional
    is_trial = False
    if expires is None:
        return LicenseStatus(
            install_id=install_id,
            expires_on=None,
            days_remaining=None,
            valid=False,
            is_trial=False,
            message="No license found. Contact MayleSoft support.",
        )

    # Re-verify stored token when present
    if token:
        try:
            tid, texp, _ = parse_license_code(token)
            if tid != install_id or texp != expires:
                return LicenseStatus(
                    install_id=install_id,
                    expires_on=expires,
                    days_remaining=None,
                    valid=False,
                    is_trial=False,
                    message="License data is corrupted. Contact MayleSoft support.",
                )
        except ValueError:
            return LicenseStatus(
                install_id=install_id,
                expires_on=expires,
                days_remaining=None,
                valid=False,
                is_trial=False,
                message="License signature invalid. Contact MayleSoft support.",
            )

    remaining = (expires - today).days
    valid = remaining >= 0
    if valid:
        if remaining <= WARN_WITHIN_DAYS:
            msg = (
                f"License expires on {expires.isoformat()} "
                f"({remaining} day(s) left). Contact {SUPPORT_CONTACT} to extend."
            )
        else:
            msg = f"Licensed until {expires.isoformat()} ({remaining} day(s) left)."
    else:
        msg = (
            f"License expired on {expires.isoformat()}. "
            f"Contact {SUPPORT_CONTACT} with Install ID {install_id} to extend usage."
        )
    return LicenseStatus(
        install_id=install_id,
        expires_on=expires,
        days_remaining=remaining,
        valid=valid,
        is_trial=is_trial,
        message=msg,
    )
