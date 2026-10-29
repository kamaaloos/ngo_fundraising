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
from app.i18n import td, tr


class UserDialog(QDialog):
    def __init__(self, parent=None, user=None, projects=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.user_title"))
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
            tr("dialog.user.password_keep")
            if self._editing
            else tr("dialog.user.password_required")
        )
        self.role = QComboBox()
        for role in USER_ROLES:
            self.role.addItem(td(role), role)
        self.is_active = QCheckBox(tr("dialog.user.active"))
        self.is_active.setChecked(True)

        layout.addRow(tr("dialog.user.username"), self.username)
        layout.addRow(tr("dialog.user.full_name"), self.full_name)
        layout.addRow(tr("dialog.user.password"), self.password)
        layout.addRow(tr("dialog.user.role"), self.role)
        layout.addRow("", self.is_active)

        layout.addRow(QLabel(tr("dialog.user.assigned")))
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

        self.role.currentIndexChanged.connect(self._on_role_changed)
        self._on_role_changed()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("common.save"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(
            tr("common.cancel")
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if user:
            self.username.setText(user.username)
            self.full_name.setText(user.full_name or "")
            role_idx = self.role.findData(user.role)
            if role_idx >= 0:
                self.role.setCurrentIndex(role_idx)
            self.is_active.setChecked(bool(user.is_active))

    def _on_role_changed(self, *_):
        enabled = self.role.currentData() != "admin"
        for check in self.project_checks.values():
            check.setEnabled(enabled)

    def validate_and_accept(self):
        if not self.username.text().strip():
            QMessageBox.warning(
                self, tr("dialog.validation"), tr("dialog.user.err_username")
            )
            return
        if not self._editing and not self.password.text():
            QMessageBox.warning(
                self, tr("dialog.validation"), tr("dialog.user.err_password")
            )
            return
        if self.role.currentData() == "user" and not self.selected_project_ids():
            QMessageBox.warning(
                self,
                tr("dialog.validation"),
                tr("dialog.user.err_projects"),
            )
            return
        self.accept()

    def selected_project_ids(self) -> list[int]:
        return [pid for pid, check in self.project_checks.items() if check.isChecked()]

    def values(self):
        data = {
            "username": self.username.text().strip(),
            "full_name": self.full_name.text().strip(),
            "role": self.role.currentData() or self.role.currentText(),
            "is_active": self.is_active.isChecked(),
        }
        if self.password.text():
            data["password"] = self.password.text()
        return data
