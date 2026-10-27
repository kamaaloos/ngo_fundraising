"""License expiry gate and extension entry (support-managed)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.branding import app_icon, copyright_label
from app.licensing import apply_license_code, get_license_status
from app.support_identity import SUPPORT_CONTACT, SUPPORT_EMAIL


class LicenseDialog(QDialog):
    """Shown when the license is missing/expired, or to enter an extension code."""

    def __init__(self, parent=None, *, blocking: bool = True):
        super().__init__(parent)
        self.setWindowTitle("App license — NGO Fundraising")
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(520)
        self.setModal(True)
        self._blocking = blocking

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(12)

        title = QLabel("Usage license")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setObjectName("muted")
        layout.addWidget(self.status)

        self.install = QLabel("")
        self.install.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.install.setObjectName("loginInstallId")
        layout.addWidget(self.install)

        tip = QLabel(
            f"To extend usage time, email {SUPPORT_EMAIL} "
            f"({SUPPORT_CONTACT}) with your Install ID. "
            "Support will send a license extension code for this computer."
        )
        tip.setWordWrap(True)
        layout.addWidget(tip)

        row = QHBoxLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText("Paste license code from MayleSoft…")
        row.addWidget(self.code, 1)
        apply_btn = QPushButton("Apply code")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self._apply)
        row.addWidget(apply_btn)
        layout.addLayout(row)

        layout.addWidget(copyright_label(object_name="loginCopyright"))

        buttons = QDialogButtonBox()
        if blocking:
            self.close_btn = buttons.addButton(
                "Quit", QDialogButtonBox.ButtonRole.RejectRole
            )
        else:
            self.close_btn = buttons.addButton(
                "Close", QDialogButtonBox.ButtonRole.RejectRole
            )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._refresh()

    def _refresh(self):
        info = get_license_status()
        self.install.setText(f"Install ID: {info.install_id}")
        if info.valid:
            self.status.setText(info.message)
            self.status.setStyleSheet("color: #176B5B; font-weight: 600;")
        else:
            self.status.setText(info.message)
            self.status.setStyleSheet("color: #B42318; font-weight: 700;")

    def _apply(self):
        code = self.code.text().strip()
        if not code:
            QMessageBox.warning(self, "License", "Paste the license code from support.")
            return
        try:
            status = apply_license_code(code)
        except Exception as exc:
            QMessageBox.critical(self, "License not applied", str(exc))
            return
        self._refresh()
        if status.valid:
            QMessageBox.information(
                self,
                "License updated",
                f"Licensed until {status.expires_on.isoformat()} "
                f"({status.days_remaining} day(s) remaining).",
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Still expired", status.message)


def ensure_license_or_exit(app) -> bool:
    """Return True if the app may continue; False if the user quit."""
    from app.licensing import ensure_trial_license

    status = ensure_trial_license()
    if status.valid:
        return True

    while True:
        dialog = LicenseDialog(blocking=True)
        result = dialog.exec()
        status = get_license_status()
        if status.valid:
            return True
        if result != QDialog.DialogCode.Accepted:
            return False
