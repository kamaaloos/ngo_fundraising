"""Show one-time recovery details for the developer to store per customer."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.support_identity import (
    SUPPORT_CONTACT,
    SUPPORT_EMAIL,
    format_support_handoff,
    generate_recovery_key,
    get_customer_name,
    get_install_id,
    persist_recovery_key,
    set_customer_name,
)


class RecoveryKeyDialog(QDialog):
    """Issues a recovery key once and asks that it be sent to the developer."""

    def __init__(self, parent=None, *, recovery_key: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Support recovery registration")
        self.setMinimumSize(520, 480)
        self.resize(560, 520)
        self.setModal(True)

        self.install_id = get_install_id()
        self.recovery_key = recovery_key or generate_recovery_key()

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Register this installation with support")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        note = QLabel(
            "Password resets and license extensions are handled by your software provider "
            f"({SUPPORT_CONTACT}).\n\n"
            f"Email {SUPPORT_EMAIL} with the Install ID and Recovery key below. "
            "They will keep the key on file. If you forget the admin password or need "
            "more usage time, email that address with your Install ID."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)

        form = QFormLayout()
        self.customer = QLineEdit(get_customer_name())
        self.customer.setPlaceholderText("Organization / customer name")
        form.addRow("Customer name", self.customer)

        self.install_edit = QLineEdit(self.install_id)
        self.install_edit.setReadOnly(True)
        form.addRow("Install ID", self.install_edit)

        self.key_edit = QLineEdit(self.recovery_key)
        self.key_edit.setReadOnly(True)
        form.addRow("Recovery key", self.key_edit)
        layout.addLayout(form)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(140)
        layout.addWidget(self.preview)
        self.customer.textChanged.connect(self._refresh_preview)
        self._refresh_preview()

        actions = QHBoxLayout()
        copy_btn = QPushButton("Copy details")
        copy_btn.clicked.connect(self._copy)
        save_btn = QPushButton("Save .txt for support…")
        save_btn.clicked.connect(self._save)
        actions.addWidget(copy_btn)
        actions.addWidget(save_btn)
        actions.addStretch()
        layout.addLayout(actions)

        warn = QLabel(
            "This recovery key is shown only once here. "
            "After you close this dialog, only support (with their copy) can unlock resets."
        )
        warn.setWordWrap(True)
        warn.setObjectName("muted")
        layout.addWidget(warn)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            "I sent this to support"
        )
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

    def _handoff_text(self) -> str:
        return format_support_handoff(
            install_id=self.install_id,
            recovery_key=self.recovery_key,
            customer_name=self.customer.text(),
        )

    def _refresh_preview(self):
        self.preview.setPlainText(self._handoff_text())

    def _copy(self):
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(self._handoff_text())
        QMessageBox.information(self, "Copied", "Support details copied to clipboard.")

    def _save(self):
        set_customer_name(self.customer.text())
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save support recovery details",
            str(Path.home() / f"NGO_recovery_{self.install_id}.txt"),
            "Text files (*.txt)",
        )
        if not path:
            return
        Path(path).write_text(self._handoff_text(), encoding="utf-8")
        QMessageBox.information(self, "Saved", f"Saved to:\n{path}")

    def _accept(self):
        set_customer_name(self.customer.text())
        if not self.customer.text().strip():
            if (
                QMessageBox.question(
                    self,
                    "Customer name",
                    "No customer name entered. Continue anyway?",
                )
                != QMessageBox.StandardButton.Yes
            ):
                return
        try:
            persist_recovery_key(self.recovery_key)
        except Exception as exc:
            QMessageBox.critical(self, "Could not save recovery key", str(exc))
            return
        QMessageBox.information(
            self,
            "Registered",
            "Recovery key saved on this PC (hash only).\n"
            f"Make sure you also emailed the plaintext key to {SUPPORT_EMAIL}.",
        )
        self.accept()
