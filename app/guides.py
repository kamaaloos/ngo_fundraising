"""Customer help guides bundled with the app."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QWidget

SHARE_GUIDE_NAME = "Share-data-between-PC-and-laptop.md"


def _package_guides_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass) / "app" / "assets" / "guides"
    return Path(__file__).resolve().parent / "assets" / "guides"


def customer_guides_dir() -> Path:
    return Path.home() / "Documents" / "NGO Fundraising" / "Guides"


def open_share_data_guide(parent: QWidget | None = None) -> Path | None:
    """Copy the PC↔laptop guide to Documents and open it."""
    source = _package_guides_dir() / SHARE_GUIDE_NAME
    if not source.is_file():
        # Fallback: short in-app steps if the file is missing.
        if parent is not None:
            QMessageBox.information(
                parent,
                "Move data between computers",
                "1. On the computer with the latest data (admin):\n"
                "   Settings → Data backup → Export backup…\n\n"
                "2. Copy the .sqlite3 file to a USB stick, email, or cloud folder.\n\n"
                "3. On the other computer (admin):\n"
                "   Settings → Data backup → Restore from backup…\n"
                "   Choose that file, confirm, then reopen the app.\n\n"
                "Restore replaces all data on the receiving computer.\n"
                "Use only one active computer after each move — there is no live sync.",
            )
        return None

    dest_dir = customer_guides_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / SHARE_GUIDE_NAME
    shutil.copy2(source, dest)
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(dest)))
    if parent is not None:
        QMessageBox.information(
            parent,
            "Move data between computers",
            "A short guide was saved and opened:\n\n"
            f"{dest}\n\n"
            "Summary: Export backup on one PC → copy the file → "
            "Restore backup on the other PC (admin). "
            "Restore replaces all data; there is no live sync.",
        )
    return dest
