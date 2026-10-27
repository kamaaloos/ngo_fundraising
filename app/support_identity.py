"""Per-installation identity for developer-managed password recovery."""

from __future__ import annotations

import secrets
import uuid

from app.db.database import get_app_meta, set_app_meta

INSTALL_ID_KEY = "install_id"
CUSTOMER_NAME_KEY = "customer_name"
SUPPORT_EMAIL = "kamaaloos@gmail.com"
SUPPORT_CONTACT = f"MayleSoft · Hasan Kamaal · {SUPPORT_EMAIL}"


def ensure_install_id() -> str:
    existing = get_app_meta(INSTALL_ID_KEY)
    if existing:
        return existing
    install_id = f"NGO-{uuid.uuid4().hex[:10].upper()}"
    set_app_meta(INSTALL_ID_KEY, install_id)
    return install_id


def get_install_id() -> str:
    return ensure_install_id()


def get_customer_name() -> str:
    return (get_app_meta(CUSTOMER_NAME_KEY) or "").strip()


def set_customer_name(name: str) -> None:
    set_app_meta(CUSTOMER_NAME_KEY, (name or "").strip())


def generate_recovery_key() -> str:
    """Return a new plaintext recovery key (does not store it)."""
    raw = secrets.token_hex(8).upper()
    return f"{raw[0:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"


def persist_recovery_key(recovery_key: str) -> None:
    """Store only the hash of the recovery key on this install."""
    from app.db.repository import set_admin_recovery_key

    set_admin_recovery_key(recovery_key)


def format_support_handoff(
    *,
    install_id: str,
    recovery_key: str,
    customer_name: str = "",
) -> str:
    org = customer_name.strip() or "(not set)"
    return (
        "NGO Fundraising — support recovery details\n"
        "----------------------------------------\n"
        f"Customer / organization: {org}\n"
        f"Install ID: {install_id}\n"
        f"Recovery key: {recovery_key}\n"
        f"Support: {SUPPORT_CONTACT}\n"
        f"Email requests to: {SUPPORT_EMAIL}\n"
        "\n"
        "Developer: store this against the customer record.\n"
        "Customer: email support with your Install ID to reset password or extend license.\n"
    )
