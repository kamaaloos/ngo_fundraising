"""Bundled import sample templates for customers.

Shipped under ``app/assets/samples`` (included in the Windows build).
Customers get editable copies under Documents — the frozen package is read-only.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QWidget


def _package_samples_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass) / "app" / "assets" / "samples"
    return Path(__file__).resolve().parent / "assets" / "samples"


def customer_samples_dir() -> Path:
    return Path.home() / "Documents" / "NGO Fundraising" / "Import samples"


def ensure_customer_samples() -> Path:
    """Copy bundled templates into Documents (overwrite missing/outdated files)."""
    source = _package_samples_dir()
    if not source.is_dir():
        raise FileNotFoundError(
            "Sample templates are missing from this install. "
            "Reinstall NGO Fundraising or contact MayleSoft support."
        )
    dest = customer_samples_dir()
    dest.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.suffix.lower() in {".csv", ".xlsx", ".md"} and path.is_file():
            target = dest / path.name
            shutil.copy2(path, target)
    return dest


def open_sample_templates(parent: QWidget | None = None) -> Path | None:
    """Copy samples to Documents and open the folder in Explorer."""
    try:
        dest = ensure_customer_samples()
    except Exception as exc:
        if parent is not None:
            QMessageBox.warning(parent, "Sample templates", str(exc))
        return None
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(dest)))
    if parent is not None:
        QMessageBox.information(
            parent,
            "Sample templates",
            "Sample CSV and Excel import files were saved here:\n\n"
            f"{dest}\n\n"
            "Use Import in Projects, Donors, or Expenses and choose a file "
            "from that folder.",
        )
    return dest
