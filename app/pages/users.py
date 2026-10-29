from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import current_session
from app.db.repository import delete_user, list_projects, list_users, save_user
from app.dialogs.user_dialog import UserDialog
from app.i18n import td, tr
from app.widgets.table_page import fill_table, make_table, selected_id


class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("contentArea")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel(tr("users.title"))
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()
        add = QPushButton(tr("users.add"))
        add.setObjectName("primaryButton")
        add.clicked.connect(self.add_user)
        top.addWidget(add)
        layout.addLayout(top)

        note = QLabel(tr("users.note"))
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.table = make_table(
            [
                tr("col.id"),
                tr("col.username"),
                tr("col.full_name"),
                tr("col.role"),
                tr("col.active"),
                tr("col.projects"),
            ]
        )
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        edit = QPushButton(tr("common.edit"))
        edit.clicked.connect(self.edit_user)
        remove = QPushButton(tr("common.delete"))
        remove.setObjectName("dangerButton")
        remove.clicked.connect(self.remove_user)
        refresh = QPushButton(tr("common.refresh"))
        refresh.clicked.connect(self.refresh)
        controls.addWidget(edit)
        controls.addWidget(remove)
        controls.addWidget(refresh)
        controls.addStretch()
        layout.addLayout(controls)

        self._users = []

    def refresh(self):
        self._users = list_users()
        fill_table(
            self.table,
            [
                (
                    u.id,
                    u.username,
                    u.full_name or "",
                    td(u.role),
                    td("Yes" if u.is_active else "No"),
                    tr("common.all")
                    if u.role == "admin"
                    else ", ".join(p.name for p in u.projects) or "—",
                )
                for u in self._users
            ],
        )

    def add_user(self):
        projects = list_projects()
        dialog = UserDialog(self, projects=projects)
        if dialog.exec():
            try:
                save_user(None, dialog.values(), dialog.selected_project_ids())
                self.refresh()
            except Exception as exc:
                QMessageBox.critical(self, tr("common.save_failed"), str(exc))

    def edit_user(self):
        user_id = selected_id(self.table)
        if user_id is None:
            QMessageBox.information(
                self, tr("users.select_title"), tr("users.select_body")
            )
            return
        user = next((u for u in self._users if u.id == user_id), None)
        if user is None:
            return
        projects = list_projects()
        dialog = UserDialog(self, user=user, projects=projects)
        if dialog.exec():
            try:
                save_user(user_id, dialog.values(), dialog.selected_project_ids())
                self.refresh()
            except Exception as exc:
                QMessageBox.critical(self, tr("common.save_failed"), str(exc))

    def remove_user(self):
        user_id = selected_id(self.table)
        if user_id is None:
            QMessageBox.information(
                self, tr("users.select_title"), tr("users.select_body")
            )
            return
        if user_id == current_session.user_id:
            QMessageBox.warning(
                self, tr("users.not_allowed"), tr("users.not_allowed_body")
            )
            return
        if (
            QMessageBox.question(
                self, tr("common.confirm_delete"), tr("users.confirm_body")
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_user(user_id)
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, tr("common.delete_failed"), str(exc))
