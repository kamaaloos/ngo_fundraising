from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

from app.db.repository import change_own_password
from app.widgets.password_edit import IconLineEdit


class ChangePasswordDialog(QDialog):
    """Forced or voluntary password change."""

    def __init__(self, user_id: int, *, forced: bool = False, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.forced = forced
        self.setWindowTitle("Change password")
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)
        note = QLabel(
            "You must set a new password before continuing."
            if forced
            else "Choose a new password (at least 8 characters)."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        form = QFormLayout()
        self.current = IconLineEdit("Current password", leading="🔒", password=True)
        self.new = IconLineEdit("New password", leading="🔒", password=True)
        self.confirm = IconLineEdit("Confirm new password", leading="🔒", password=True)
        form.addRow("Current", self.current)
        form.addRow("New", self.new)
        form.addRow("Confirm", self.confirm)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._submit)
        buttons.rejected.connect(self.reject)
        if forced:
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Sign out")
        layout.addWidget(buttons)

    def _submit(self):
        new_password = self.new.text()
        if new_password != self.confirm.text():
            QMessageBox.warning(self, "Mismatch", "New passwords do not match.")
            return
        if new_password == self.current.text():
            QMessageBox.warning(
                self, "Password", "New password must be different from the current one."
            )
            return
        try:
            change_own_password(self.user_id, self.current.text(), new_password)
        except Exception as exc:
            QMessageBox.warning(self, "Could not change password", str(exc))
            return
        self.accept()
