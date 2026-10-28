from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QWidget,
)

from app.auth.session import current_session
from app.branding import COPYRIGHT_TEXT, app_icon, apply_windows_titlebar_theme
from app.dialogs.license_dialog import LicenseDialog
from app.i18n import tr
from app.licensing import get_license_status
from app.db.database import (
    days_since_last_backup,
    export_database_backup,
    local_backup_destination,
)
from app.db.repository import get_project
from app.pages.donations import DonationsPage
from app.pages.donors import DonorsPage
from app.pages.expenses import ExpensesPage
from app.pages.overview import OverviewPage
from app.pages.project_dashboard import ProjectDashboardPage
from app.pages.projects import ProjectsPage
from app.pages.reports import ReportsPage
from app.pages.settings import SettingsPage
from app.pages.users import UsersPage
from app.settings_store import THEME_PRESETS, load_settings
from app.styles import build_stylesheet
from app.windowing import fit_window
from app.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    """session_ended(True) = return to login; False = quit app."""

    session_ended = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app.name"))
        self.setWindowIcon(app_icon())
        self._ending = False
        self._to_login = False
        self._frame_theme_applied = False
        self._backup_reminder_shown = False
        self._fit_to_screen()

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_selected.connect(self._navigate)
        self.sidebar.logout_requested.connect(self._logout)
        root_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

        self.page_keys: list[str] = []
        self._build_pages()
        self._configure_nav()
        self.refresh_all()
        self.statusBar().showMessage(tr("common.ready"))
        lic = get_license_status()
        self._license_btn = QPushButton(lic.message if lic.expires_on else "License")
        self._license_btn.setObjectName("loginForgotLink")
        self._license_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._license_btn.setFlat(True)
        self._license_btn.clicked.connect(self._open_license_dialog)
        self.statusBar().addPermanentWidget(self._license_btn)
        copyright = QLabel(COPYRIGHT_TEXT)
        copyright.setObjectName("statusCopyright")
        self.statusBar().addPermanentWidget(copyright)

    def _open_license_dialog(self):
        LicenseDialog(self, blocking=False).exec()
        lic = get_license_status()
        self._license_btn.setText(lic.message if lic.expires_on else "License")
        if not lic.valid:
            QMessageBox.warning(
                self,
                "License expired",
                lic.message + "\n\nThe app will close after you sign out.",
            )

    def _build_pages(self):
        self.overview = OverviewPage(on_open_project=self.open_project)
        self.projects_page = ProjectsPage(
            on_changed=self.refresh_all,
            on_open_project=self.open_project,
        )
        self.project_dashboard = ProjectDashboardPage()
        self.donors_page = DonorsPage(on_changed=self.refresh_project_views)
        self.donations_page = DonationsPage(on_changed=self.refresh_project_views)
        self.expenses_page = ExpensesPage(on_changed=self.refresh_project_views)
        self.reports_page = ReportsPage()
        self.users_page = UsersPage()
        self.settings_page = SettingsPage()
        self.settings_page.appearance_changed.connect(self._apply_appearance)

        self._pages = {
            "Overview": self.overview,
            "Projects": self.projects_page,
            "Dashboard": self.project_dashboard,
            "Donors": self.donors_page,
            "Donations": self.donations_page,
            "Expenses": self.expenses_page,
            "Reports": self.reports_page,
            "Users": self.users_page,
            "Settings": self.settings_page,
        }

        for key, page in self._pages.items():
            self.stack.addWidget(page)
            self.page_keys.append(key)

    def _configure_nav(self):
        display = current_session.full_name or current_session.username
        self.sidebar.set_user(display, current_session.role)

        pages = [
            ("Overview", tr("nav.overview")),
            ("Projects", tr("nav.projects")),
            ("Dashboard", tr("nav.dashboard")),
            ("Donors", tr("nav.donors")),
            ("Donations", tr("nav.donations")),
            ("Expenses", tr("nav.expenses")),
            ("Reports", tr("nav.reports")),
        ]
        if current_session.is_admin:
            pages.append(("Users", tr("nav.users")))
        pages.append(("Settings", tr("nav.settings")))

        self.sidebar.set_pages(pages)
        self._navigate("Overview")

    def _apply_appearance(self):
        from PySide6.QtWidgets import QApplication

        qapp = QApplication.instance()
        if qapp is not None:
            qapp.setStyleSheet(build_stylesheet())
        self.sidebar.refresh_user_logo()
        self.settings_page.refresh()
        self._sync_windows_titlebar()

    def _sync_windows_titlebar(self):
        settings = load_settings()
        accent = THEME_PRESETS[settings.accent_key()]["accent"]
        dark = settings.mode_key() == "night"
        # Day mode: tint caption with a deep shade of the accent; night: near-black accent.
        caption = accent if dark else accent
        apply_windows_titlebar_theme(self, dark=dark, caption_hex=caption)

    def _fit_to_screen(self):
        """Open within the usable desktop area (avoids taskbar overflow)."""
        fit_window(
            self,
            prefer_width=1180,
            prefer_height=700,
            min_width=900,
            min_height=560,
            height_ratio=0.90,
        )

    def showEvent(self, event):
        super().showEvent(event)
        if not self._frame_theme_applied:
            self._frame_theme_applied = True
            # winId is valid after the native window exists.
            self._sync_windows_titlebar()
            # Re-fit after native frame chrome is applied (packaged builds).
            self._fit_to_screen()
        self._maybe_remind_backup()

    def _maybe_remind_backup(self):
        if self._backup_reminder_shown or not current_session.is_admin:
            return
        settings = load_settings()
        days = days_since_last_backup()
        threshold = settings.backup_reminder_days
        if days is not None and days < threshold:
            return
        self._backup_reminder_shown = True
        if days is None:
            body = tr("backup.reminder_none")
        else:
            body = tr("backup.reminder_days", days=days)
        QMessageBox.information(self, tr("backup.reminder_title"), body)

    def _run_exit_backup(self) -> None:
        if not current_session.is_admin or self._to_login:
            return
        settings = load_settings()
        if not settings.backup_on_exit:
            return
        try:
            export_database_backup(local_backup_destination())
        except Exception:
            pass

    def _navigate(self, page_name: str):
        requires_project = {"Dashboard", "Donors", "Donations", "Expenses"}
        # Non-admins still need a project for Reports; admins get Overall view.
        if not current_session.is_admin:
            requires_project.add("Reports")

        if page_name in requires_project and current_session.current_project_id is None:
            QMessageBox.information(
                self,
                "Select a project",
                "Open a project from Overview or Projects first.",
            )
            self.sidebar.select_page("Overview")
            page_name = "Overview"

        if page_name not in self._pages:
            return
        if page_name == "Users" and not current_session.is_admin:
            return

        if page_name == "Reports":
            self.reports_page.set_project(current_session.current_project_id)

        index = self.page_keys.index(page_name)
        self.stack.setCurrentIndex(index)
        self.sidebar.select_page(page_name)

    def open_project(self, project_id: int):
        if not current_session.can_access_project(project_id):
            QMessageBox.warning(
                self, "Access denied", "You are not assigned to this project."
            )
            return

        project = get_project(project_id)
        if project is None:
            QMessageBox.warning(self, "Not found", "Project no longer exists.")
            return

        current_session.current_project_id = project_id
        self.sidebar.set_project_name(project.name)
        self.project_dashboard.set_project(project_id)
        self.donors_page.set_project(project_id)
        self.donations_page.set_project(project_id)
        self.expenses_page.set_project(project_id)
        self.reports_page.set_project(project_id)
        self.statusBar().showMessage(f"Working on: {project.name}", 4000)
        self._navigate("Dashboard")

    def refresh_project_views(self):
        pid = current_session.current_project_id
        self.project_dashboard.set_project(pid)
        self.donors_page.set_project(pid)
        self.donations_page.set_project(pid)
        self.expenses_page.set_project(pid)
        self.reports_page.set_project(pid)
        self.overview.refresh()
        self.projects_page.refresh()
        if pid:
            project = get_project(pid)
            if project:
                self.sidebar.set_project_name(project.name)

    def refresh_all(self):
        self.overview.refresh()
        self.projects_page.refresh()
        if current_session.is_admin:
            self.users_page.refresh()
        self.refresh_project_views()

    def _logout(self):
        if (
            QMessageBox.question(self, tr("logout.title"), tr("logout.confirm"))
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._to_login = True
        self.close()

    def closeEvent(self, event: QCloseEvent):
        # Guard against Ctrl+C / teardown races while closing.
        try:
            if not self._ending:
                self._ending = True
                self._run_exit_backup()
                to_login = self._to_login
                current_session.clear()
                self.session_ended.emit(to_login)
        except Exception:
            pass
        event.accept()
