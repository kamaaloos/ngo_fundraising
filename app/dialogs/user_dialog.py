from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.db.models import USER_ROLES


class UserDialog(QDialog):
    def __init__(self, parent=None, user=None, projects=None):
        super().__init__(parent)
        self.setWindowTitle("User account")
        self.setMinimumWidth(460)
        self.setMinimumHeight(420)
        projects = projects or []
        self._editing = user is not None

        layout = QFormLayout(self)
        self.username = QLineEdit()
        self.full_name = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText(
            "Leave blank to keep current" if self._editing else "Required"
        )
        self.role = QComboBox()
        self.role.addItems(list(USER_ROLES))
        self.is_active = QCheckBox("Active account")
        self.is_active.setChecked(True)

        layout.addRow("Username *", self.username)
        layout.addRow("Full name", self.full_name)
        layout.addRow("Password", self.password)
        layout.addRow("Role", self.role)
        layout.addRow("", self.is_active)

        layout.addRow(QLabel("Assigned projects (for users):"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(140)
        host = QWidget()
        self.project_box = QVBoxLayout(host)
        self.project_checks: dict[int, QCheckBox] = {}
        assigned = {p.id for p in (user.projects if user else [])}
        for project in projects:
            check = QCheckBox(project.name)
            check.setChecked(project.id in assigned)
            self.project_checks[project.id] = check
            self.project_box.addWidget(check)
        self.project_box.addStretch()
        scroll.setWidget(host)
        layout.addRow(scroll)

        self.role.currentTextChanged.connect(self._on_role_changed)
        self._on_role_changed(self.role.currentText())

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if user:
            self.username.setText(user.username)
            self.full_name.setText(user.full_name or "")
            self.role.setCurrentText(user.role)
            self.is_active.setChecked(bool(user.is_active))

    def _on_role_changed(self, role: str):
        enabled = role != "admin"
        for check in self.project_checks.values():
            check.setEnabled(enabled)

    def validate_and_accept(self):
        if not self.username.text().strip():
            QMessageBox.warning(self, "Validation", "Username is required.")
            return
        if not self._editing and not self.password.text():
            QMessageBox.warning(self, "Validation", "Password is required for new users.")
            return
        if self.role.currentText() == "user" and not self.selected_project_ids():
            QMessageBox.warning(
                self,
                "Validation",
                "Assign at least one project to a non-admin user.",
            )
            return
        self.accept()

    def selected_project_ids(self) -> list[int]:
        return [pid for pid, check in self.project_checks.items() if check.isChecked()]

    def values(self):
        data = {
            "username": self.username.text().strip(),
            "full_name": self.full_name.text().strip(),
            "role": self.role.currentText(),
            "is_active": self.is_active.isChecked(),
        }
        if self.password.text():
            data["password"] = self.password.text()
        return data
