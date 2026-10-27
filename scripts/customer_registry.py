"""
Developer registry: customer Install IDs, recovery keys, and license expiry.

Store this file only on the developer's machine (do not ship to customers).

Usage (from project folder, venv active):

    python scripts/customer_registry.py add --name "Green Hope NGO" --install-id NGO-ABC123DEF0 --recovery-key ABCD-EF01-2345-6789
    python scripts/customer_registry.py list
    python scripts/customer_registry.py find --install-id NGO-ABC123DEF0

    # Issue / extend usage time (prints a license code for the customer):
    python scripts/customer_registry.py extend --install-id NGO-ABC123DEF0 --days 365
    python scripts/customer_registry.py extend --install-id NGO-ABC123DEF0 --until 2027-12-31
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.licensing import build_license_code

# Keep secrets on the developer PC, not in the customer app data folder.
REGISTRY_PATH = (
    Path.home() / "AppData" / "Local" / "MayleSoftSupport" / "customer_registry.json"
)


def _load() -> list[dict]:
    if not REGISTRY_PATH.exists():
        return []
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return list(data.get("customers", []))


def _save(customers: list[dict]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "customers": customers,
    }
    REGISTRY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _find_row(customers: list[dict], install_id: str) -> dict | None:
    needle = install_id.strip().upper()
    for row in customers:
        if row.get("install_id", "").upper() == needle:
            return row
    return None


def cmd_add(args: argparse.Namespace) -> int:
    customers = _load()
    install_id = args.install_id.strip().upper()
    row = _find_row(customers, install_id)
    if row is not None:
        row["name"] = args.name.strip()
        row["recovery_key"] = args.recovery_key.strip().upper()
        row["notes"] = (args.notes or "").strip()
        row["updated_at"] = datetime.now(timezone.utc).isoformat()
        _save(customers)
        print(f"Updated existing customer {install_id}")
        print(f"Registry: {REGISTRY_PATH}")
        return 0

    customers.append(
        {
            "name": args.name.strip(),
            "install_id": install_id,
            "recovery_key": args.recovery_key.strip().upper(),
            "license_expires_on": "",
            "notes": (args.notes or "").strip(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    _save(customers)
    print(f"Added customer {args.name.strip()} ({install_id})")
    print(f"Registry: {REGISTRY_PATH}")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    customers = _load()
    if not customers:
        print(f"No customers yet. Registry path: {REGISTRY_PATH}")
        return 0
    print(f"Registry: {REGISTRY_PATH}\n")
    for row in customers:
        print(
            f"- {row.get('name')} | {row.get('install_id')} | "
            f"key={row.get('recovery_key')} | "
            f"license={row.get('license_expires_on') or '—'}"
        )
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    customers = _load()
    needle_id = (args.install_id or "").strip().upper()
    needle_name = (args.name or "").strip().lower()
    hits = []
    for row in customers:
        if needle_id and row.get("install_id", "").upper() == needle_id:
            hits.append(row)
        elif needle_name and needle_name in (row.get("name") or "").lower():
            hits.append(row)
    if not hits:
        print("No match.")
        return 1
    for row in hits:
        print(f"Customer:     {row.get('name')}")
        print(f"Install ID:   {row.get('install_id')}")
        print(f"Recovery key: {row.get('recovery_key')}")
        print(f"License until:{row.get('license_expires_on') or '—'}")
        if row.get("notes"):
            print(f"Notes:        {row.get('notes')}")
        print("---")
    print(
        "Password reset: customer enters recovery key on Sign in.\n"
        "License extend: use `extend` then send them the printed license code."
    )
    return 0


def cmd_extend(args: argparse.Namespace) -> int:
    customers = _load()
    install_id = args.install_id.strip().upper()
    row = _find_row(customers, install_id)
    if row is None and not args.force:
        print(
            f"Install ID {install_id} is not in the registry. "
            "Add the customer first, or pass --force."
        )
        return 1

    if args.until:
        try:
            expires = date.fromisoformat(args.until)
        except ValueError:
            print("--until must be YYYY-MM-DD")
            return 1
    else:
        days = int(args.days)
        if days < 1:
            print("--days must be >= 1")
            return 1
        base = date.today()
        if row and row.get("license_expires_on"):
            try:
                current = date.fromisoformat(row["license_expires_on"])
                if current > base:
                    base = current
            except ValueError:
                pass
        expires = base + timedelta(days=days)

    code = build_license_code(install_id, expires)
    if row is not None:
        row["license_expires_on"] = expires.isoformat()
        row["updated_at"] = datetime.now(timezone.utc).isoformat()
        if args.name:
            row["name"] = args.name.strip()
        _save(customers)
    elif args.force:
        customers.append(
            {
                "name": (args.name or install_id).strip(),
                "install_id": install_id,
                "recovery_key": "",
                "license_expires_on": expires.isoformat(),
                "notes": "Created via extend --force",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        _save(customers)

    print(f"Customer:     {(row or {}).get('name') or args.name or install_id}")
    print(f"Install ID:   {install_id}")
    print(f"Licensed until: {expires.isoformat()}")
    print(f"License code:\n{code}")
    print(
        "\nTell the customer to open the app → license / Sign in screen → "
        "paste this code under Apply / Enter license code."
    )
    print(f"Registry: {REGISTRY_PATH}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MayleSoft developer registry (recovery + license)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add or update a customer record")
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--install-id", required=True)
    add_p.add_argument("--recovery-key", required=True)
    add_p.add_argument("--notes", default="")
    add_p.set_defaults(func=cmd_add)

    list_p = sub.add_parser("list", help="List all registered customers")
    list_p.set_defaults(func=cmd_list)

    find_p = sub.add_parser("find", help="Look up recovery / license for a customer")
    find_p.add_argument("--install-id", default="")
    find_p.add_argument("--name", default="")
    find_p.set_defaults(func=cmd_find)

    ext_p = sub.add_parser("extend", help="Issue a license extension code")
    ext_p.add_argument("--install-id", required=True)
    ext_p.add_argument("--days", type=int, default=365, help="Days to add (default 365)")
    ext_p.add_argument("--until", default="", help="Absolute end date YYYY-MM-DD")
    ext_p.add_argument("--name", default="", help="Optional name when using --force")
    ext_p.add_argument(
        "--force",
        action="store_true",
        help="Allow extend even if install id is not in the registry yet",
    )
    ext_p.set_defaults(func=cmd_extend)

    args = parser.parse_args()
    if args.command == "find" and not args.install_id and not args.name:
        print("Provide --install-id and/or --name")
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
