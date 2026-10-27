from __future__ import annotations

import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.db.models import PROJECT_STATUSES
from app.db.repository import normalize_project_status
from app.db.repository import (
    find_or_create_donor,
    get_project,
    list_projects,
    save_donation,
    save_donor,
    save_project,
)


def _norm_header(value: str) -> str:
    return (value or "").strip().lower().replace(" ", "_")


def _read_rows(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = []
            for raw in reader:
                rows.append({_norm_header(k): (v or "").strip() for k, v in raw.items()})
            return rows

    if suffix in {".xlsx", ".xlsm", ".xls"}:
        from openpyxl import load_workbook

        workbook = load_workbook(path, read_only=True, data_only=True)
        sheet = workbook.active
        rows_iter = sheet.iter_rows(values_only=True)
        headers = [_norm_header(str(h or "")) for h in next(rows_iter)]
        rows = []
        for values in rows_iter:
            if values is None or all(v is None or str(v).strip() == "" for v in values):
                continue
            row = {}
            for key, value in zip(headers, values):
                if not key:
                    continue
                row[key] = "" if value is None else str(value).strip()
            rows.append(row)
        return rows

    raise ValueError("Unsupported file type. Use CSV or Excel (.xlsx).")


def _pick(row: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        if row.get(key):
            return row[key]
    return ""


def _parse_money(value: str, default: str = "0") -> Decimal:
    text = (value or default).replace(",", "").strip()
    if not text:
        text = default
    try:
        amount = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid amount '{value}'") from exc
    if amount < 0:
        raise ValueError("amount cannot be negative")
    return amount


def _parse_date(value: str) -> date:
    text = (value or "").strip()
    if not text:
        return date.today()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid date '{value}' (use YYYY-MM-DD)")


DONOR_ALIASES = {
    "name": ("name", "donor", "donor_name", "full_name"),
    "email": ("email", "e_mail", "mail"),
    "phone": ("phone", "mobile", "tel", "telephone"),
    "address": ("address", "location"),
    "notes": ("notes", "note", "remark", "remarks"),
}

PROJECT_ALIASES = {
    "name": ("name", "project", "project_name", "title"),
    "description": ("description", "desc", "details"),
    "target": ("target", "target_amount", "goal", "fundraising_goal"),
    "status": ("status", "project_status"),
}

DONATION_ALIASES = {
    "pledged": ("pledged", "pledged_amount", "raised", "amount", "commitment"),
    "paid": ("paid", "paid_amount", "received"),
    "method": ("method", "payment_method", "payment"),
    "date": ("date", "donation_date", "pledged_date"),
    "reference": ("reference", "ref", "receipt"),
}


def import_donors_from_file(path: str | Path) -> tuple[int, list[str]]:
    """Import global donors. Columns: name*, email, phone, address, notes."""
    rows = _read_rows(Path(path))
    created = 0
    warnings: list[str] = []

    for index, row in enumerate(rows, start=2):
        name = _pick(row, DONOR_ALIASES["name"])
        if not name:
            warnings.append(f"Row {index}: skipped (missing name)")
            continue
        values = {
            "name": name,
            "email": _pick(row, DONOR_ALIASES["email"]),
            "phone": _pick(row, DONOR_ALIASES["phone"]),
            "address": _pick(row, DONOR_ALIASES["address"]),
            "notes": _pick(row, DONOR_ALIASES["notes"]),
        }
        try:
            save_donor(None, values)
            created += 1
        except Exception as exc:
            warnings.append(f"Row {index}: {exc}")

    return created, warnings


def import_projects_from_file(path: str | Path) -> tuple[int, list[str]]:
    """
    Import projects.
    Columns: name*, description, target/target_amount/goal, status
    """
    rows = _read_rows(Path(path))
    created = 0
    warnings: list[str] = []
    existing_names = {p.name.strip().lower() for p in list_projects()}

    for index, row in enumerate(rows, start=2):
        name = _pick(row, PROJECT_ALIASES["name"])
        if not name:
            warnings.append(f"Row {index}: skipped (missing project name)")
            continue
        if name.strip().lower() in existing_names:
            warnings.append(f"Row {index}: skipped (project '{name}' already exists)")
            continue

        status = normalize_project_status(
            _pick(row, PROJECT_ALIASES["status"]) or "Active"
        )
        if status not in PROJECT_STATUSES:
            status = "Active"

        try:
            target = _parse_money(_pick(row, PROJECT_ALIASES["target"]), "0")
            if target <= 0:
                warnings.append(f"Row {index}: skipped (target must be > 0)")
                continue
            save_project(
                None,
                {
                    "name": name,
                    "description": _pick(row, PROJECT_ALIASES["description"]),
                    "target_amount": target,
                    "status": status,
                },
            )
            existing_names.add(name.strip().lower())
            created += 1
        except Exception as exc:
            warnings.append(f"Row {index}: {exc}")

    return created, warnings


def import_donors_linked_to_project(
    path: str | Path,
    project_id: int,
) -> tuple[int, int, int, list[str]]:
    """
    Import donors and link them to a project via donation records.

    Columns:
      name* (or donor_name), email, phone, address, notes,
      pledged/pledged_amount/amount (optional, default 0 → still links with Pending),
      paid/paid_amount, method/payment_method, date/donation_date, reference

    Returns (donors_created, donors_reused, donations_created, warnings)
    """
    project = get_project(project_id)
    if project is None:
        raise ValueError("Project not found")

    rows = _read_rows(Path(path))
    donors_created = 0
    donors_reused = 0
    donations_created = 0
    warnings: list[str] = []

    for index, row in enumerate(rows, start=2):
        name = _pick(row, DONOR_ALIASES["name"])
        if not name:
            warnings.append(f"Row {index}: skipped (missing donor name)")
            continue

        donor_values = {
            "name": name,
            "email": _pick(row, DONOR_ALIASES["email"]),
            "phone": _pick(row, DONOR_ALIASES["phone"]),
            "address": _pick(row, DONOR_ALIASES["address"]),
            "notes": _pick(row, DONOR_ALIASES["notes"]),
        }

        try:
            donor_id, created = find_or_create_donor(donor_values)
            if created:
                donors_created += 1
            else:
                donors_reused += 1

            pledged_raw = _pick(row, DONATION_ALIASES["pledged"])
            paid_raw = _pick(row, DONATION_ALIASES["paid"])
            # Link even without amounts: use 0.01 pledged pending if nothing given?
            # Better: if no pledged, create a zero-pledge Pending link with pledged=0.01
            # User said "link donors" - use pledged default 0 and paid 0 → status Pending.
            # But our donation validation requires pledged > 0 in the UI. Model allows 0?
            # compute_donation_status with 0,0 → Pending. DonationDialog requires > 0.
            # For import, allow pledged 0 as a soft link: use Decimal("0.00")
            pledged = _parse_money(pledged_raw, "0") if pledged_raw else Decimal("0.00")
            paid = _parse_money(paid_raw, "0") if paid_raw else Decimal("0.00")
            if paid > pledged and pledged > 0:
                warnings.append(
                    f"Row {index}: paid capped to pledged ({paid} → {pledged})"
                )
                paid = pledged
            if pledged <= 0 and paid > 0:
                pledged = paid

            # Minimum link amount so the donor appears in project donor filter
            if pledged <= 0 and paid <= 0:
                pledged = Decimal("0.00")
                paid = Decimal("0.00")

            save_donation(
                None,
                {
                    "donor_id": donor_id,
                    "project_id": project_id,
                    "pledged_amount": pledged if pledged > 0 else Decimal("0.01"),
                    "paid_amount": paid,
                    "donation_date": _parse_date(_pick(row, DONATION_ALIASES["date"])),
                    "payment_method": _pick(row, DONATION_ALIASES["method"]) or "Cash",
                    "reference": _pick(row, DONATION_ALIASES["reference"]),
                    "notes": _pick(row, DONOR_ALIASES["notes"])
                    or (
                        "Linked via import"
                        if pledged <= 0 and not pledged_raw
                        else ""
                    ),
                },
            )
            donations_created += 1
        except Exception as exc:
            warnings.append(f"Row {index}: {exc}")

    return donors_created, donors_reused, donations_created, warnings


def import_projects_with_donors_from_file(
    path: str | Path,
) -> tuple[int, int, int, list[str]]:
    """
    Combined sheet: create/find projects and link donors in one file.

    Columns:
      project_name*, target/goal (required when creating), status, description,
      donor_name*, email, phone, pledged, paid, method, date, reference

    Returns (projects_created, donors_created, donations_created, warnings)
    """
    rows = _read_rows(Path(path))
    projects_created = 0
    donors_created = 0
    donations_created = 0
    warnings: list[str] = []

    # Cache by lowercase name
    project_map = {p.name.strip().lower(): p.id for p in list_projects()}

    for index, row in enumerate(rows, start=2):
        project_name = _pick(row, PROJECT_ALIASES["name"])
        donor_name = _pick(row, DONOR_ALIASES["name"])
        if not project_name:
            warnings.append(f"Row {index}: skipped (missing project name)")
            continue
        if not donor_name:
            warnings.append(f"Row {index}: skipped (missing donor name)")
            continue

        try:
            key = project_name.strip().lower()
            if key not in project_map:
                target = _parse_money(_pick(row, PROJECT_ALIASES["target"]), "0")
                if target <= 0:
                    warnings.append(
                        f"Row {index}: skipped (new project needs target > 0)"
                    )
                    continue
                status = normalize_project_status(
                    _pick(row, PROJECT_ALIASES["status"]) or "Active"
                )
                if status not in PROJECT_STATUSES:
                    status = "Active"
                project_id = save_project(
                    None,
                    {
                        "name": project_name,
                        "description": _pick(row, PROJECT_ALIASES["description"]),
                        "target_amount": target,
                        "status": status,
                    },
                )
                project_map[key] = project_id
                projects_created += 1
            else:
                project_id = project_map[key]

            donor_id, created = find_or_create_donor(
                {
                    "name": donor_name,
                    "email": _pick(row, DONOR_ALIASES["email"]),
                    "phone": _pick(row, DONOR_ALIASES["phone"]),
                    "address": _pick(row, DONOR_ALIASES["address"]),
                    "notes": _pick(row, DONOR_ALIASES["notes"]),
                }
            )
            if created:
                donors_created += 1

            pledged_raw = _pick(row, DONATION_ALIASES["pledged"])
            paid_raw = _pick(row, DONATION_ALIASES["paid"])
            pledged = _parse_money(pledged_raw, "0") if pledged_raw else Decimal("0.00")
            paid = _parse_money(paid_raw, "0") if paid_raw else Decimal("0.00")
            if paid > pledged and pledged > 0:
                paid = pledged
            if pledged <= 0 and paid > 0:
                pledged = paid
            if pledged <= 0:
                pledged = Decimal("0.01")

            save_donation(
                None,
                {
                    "donor_id": donor_id,
                    "project_id": project_id,
                    "pledged_amount": pledged,
                    "paid_amount": paid,
                    "donation_date": _parse_date(_pick(row, DONATION_ALIASES["date"])),
                    "payment_method": _pick(row, DONATION_ALIASES["method"]) or "Cash",
                    "reference": _pick(row, DONATION_ALIASES["reference"]),
                    "notes": _pick(row, DONOR_ALIASES["notes"]) or "Linked via import",
                },
            )
            donations_created += 1
        except Exception as exc:
            warnings.append(f"Row {index}: {exc}")

    return projects_created, donors_created, donations_created, warnings
