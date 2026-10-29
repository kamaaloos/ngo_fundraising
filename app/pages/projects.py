from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import current_session
from app.db.models import PROJECT_STATUSES
from app.db.repository import delete_project, list_projects, save_project
from app.dialogs.project_dialog import ProjectDialog
from app.i18n import td, tr
from app.io.importers import (
    import_projects_from_file,
    import_projects_with_donors_from_file,
)
from app.utils import money
from app.widgets.table_page import fill_table, make_table, selected_id


class ProjectsPage(QWidget):
    def __init__(self, on_changed=None, on_open_project=None):
        super().__init__()
        self.on_changed = on_changed
        self.on_open_project = on_open_project
        self.setObjectName("contentArea")
        self._projects = []
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(220)
        self._search_timer.timeout.connect(self.refresh)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel(tr("projects.title"))
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()
        self.import_btn = QPushButton(tr("projects.import"))
        self.import_btn.setObjectName("ghostButton")
        self.import_btn.clicked.connect(self.import_projects)
        self.import_linked_btn = QPushButton(tr("projects.import_linked"))
        self.import_linked_btn.setObjectName("ghostButton")
        self.import_linked_btn.clicked.connect(self.import_projects_with_donors)
        self.add_btn = QPushButton(tr("projects.add"))
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.add_project)
        top.addWidget(self.import_btn)
        top.addWidget(self.import_linked_btn)
        top.addWidget(self.add_btn)
        layout.addLayout(top)

        note = QLabel(tr("projects.note"))
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("projects.search_ph"))
        self.search.textChanged.connect(self._on_search_changed)
        filters.addWidget(self.search, 1)

        filters.addWidget(QLabel(tr("projects.status_filter")))
        self.status_combo = QComboBox()
        self.status_combo.addItem(tr("projects.current"), "__current__")
        self.status_combo.addItem(tr("projects.all_statuses"), "")
        for status in PROJECT_STATUSES:
            self.status_combo.addItem(td(status), status)
        self.status_combo.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.status_combo)
        layout.addLayout(filters)

        self.result_label = QLabel("")
        self.result_label.setObjectName("muted")
        layout.addWidget(self.result_label)

        self.table = make_table(
            [
                tr("col.id"),
                tr("col.name"),
                tr("col.target"),
                tr("col.raised"),
                tr("col.expenses"),
                tr("col.fund_status"),
                tr("col.status"),
            ]
        )
        self.table.doubleClicked.connect(self._open_selected)
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        open_btn = QPushButton(tr("projects.open_dashboard"))
        open_btn.clicked.connect(self._open_selected)
        self.edit_btn = QPushButton(tr("common.edit"))
        self.edit_btn.clicked.connect(self.edit_project)
        self.remove_btn = QPushButton(tr("common.delete"))
        self.remove_btn.setObjectName("dangerButton")
        self.remove_btn.clicked.connect(self.remove_project)
        refresh = QPushButton(tr("common.refresh"))
        refresh.clicked.connect(self.refresh)
        controls.addWidget(open_btn)
        controls.addWidget(self.edit_btn)
        controls.addWidget(self.remove_btn)
        controls.addWidget(refresh)
        controls.addStretch()
        layout.addLayout(controls)

    def _on_search_changed(self, *_):
        self._search_timer.start()

    def _notify(self):
        if self.on_changed:
            self.on_changed()

    def _open_selected(self):
        project_id = selected_id(self.table)
        if project_id and self.on_open_project:
            self.on_open_project(project_id)

    def refresh(self):
        status = self.status_combo.currentData()
        include_archived = True
        status_filter = None
        if status == "__current__":
            include_archived = False
        elif status:
            status_filter = status
        self._projects = list_projects(
            role=current_session.role,
            project_ids=current_session.project_ids,
            search=self.search.text(),
            status=status_filter,
            include_archived=include_archived,
        )
        fill_table(
            self.table,
            [
                (
                    p.id,
                    p.name,
                    money(p.target_amount),
                    money(p.amount_raised),
                    money(p.total_expenses),
                    td(p.fundraising_status),
                    td(p.status),
                )
                for p in self._projects
            ],
        )
        self.result_label.setText(tr("projects.count", count=len(self._projects)))
        self.add_btn.setVisible(current_session.is_admin)
        self.import_btn.setVisible(current_session.is_admin)
        self.import_linked_btn.setVisible(current_session.is_admin)
        self.edit_btn.setVisible(current_session.is_admin)
        self.remove_btn.setVisible(current_session.is_admin)

    def _show_import_result(self, title: str, message: str, warnings: list[str]):
        if warnings:
            preview = "\n".join(warnings[:8])
            more = "" if len(warnings) <= 8 else f"\n… and {len(warnings) - 8} more"
            message += f"\n\nNotes:\n{preview}{more}"
        QMessageBox.information(self, title, message)

    def import_projects(self):
        if not current_session.is_admin:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("projects.import"),
            "",
            "Spreadsheets (*.csv *.xlsx);;CSV (*.csv);;Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            created, warnings = import_projects_from_file(path)
        except Exception as exc:
            QMessageBox.critical(self, tr("donors.import_failed"), str(exc))
            return
        self._show_import_result(
            tr("donors.import_complete"),
            f"Created {created} project(s).\n\n"
            "Columns: name, description, target (or goal), status",
            warnings,
        )
        self.refresh()
        self._notify()

    def import_projects_with_donors(self):
        if not current_session.is_admin:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("projects.import_linked"),
            "",
            "Spreadsheets (*.csv *.xlsx);;CSV (*.csv);;Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            projects, donors, donations, warnings = import_projects_with_donors_from_file(
                path
            )
        except Exception as exc:
            QMessageBox.critical(self, tr("donors.import_failed"), str(exc))
            return
        self._show_import_result(
            tr("donors.import_complete"),
            f"Projects created: {projects}\n"
            f"Donors created: {donors}\n"
            f"Donations linked: {donations}\n\n"
            "Columns: project_name, target, status, donor_name, email, phone, "
            "pledged, paid, method, date",
            warnings,
        )
        self.refresh()
        self._notify()

    def add_project(self):
        if not current_session.is_admin:
            return
        dialog = ProjectDialog(self)
        if dialog.exec():
            try:
                save_project(None, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, tr("common.save_failed"), str(exc))

    def edit_project(self):
        if not current_session.is_admin:
            QMessageBox.information(
                self, tr("common.permission"), tr("projects.permission_edit")
            )
            return
        project_id = selected_id(self.table)
        if project_id is None:
            QMessageBox.information(
                self, tr("projects.select_title"), tr("projects.select_body")
            )
            return
        project = next((p for p in self._projects if p.id == project_id), None)
        if project is None:
            return
        dialog = ProjectDialog(self, project)
        if dialog.exec():
            try:
                save_project(project_id, dialog.values())
                self.refresh()
                self._notify()
            except Exception as exc:
                QMessageBox.critical(self, tr("common.save_failed"), str(exc))

    def remove_project(self):
        if not current_session.is_admin:
            QMessageBox.information(
                self, tr("common.permission"), tr("projects.permission_delete")
            )
            return
        project_id = selected_id(self.table)
        if project_id is None:
            QMessageBox.information(
                self, tr("projects.select_title"), tr("projects.select_body")
            )
            return
        if (
            QMessageBox.question(
                self,
                tr("common.confirm_delete"),
                tr("projects.confirm_body"),
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_project(project_id)
            if current_session.current_project_id == project_id:
                current_session.current_project_id = None
            self.refresh()
            self._notify()
        except Exception as exc:
            QMessageBox.critical(self, tr("common.delete_failed"), str(exc))
