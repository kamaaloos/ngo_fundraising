import os
import signal
import sys

# Mute noisy Windows DirectWrite warnings for legacy bitmap fonts
# (8514oem, Fixedsys, Modern, MS Sans Serif, MS Serif). Harmless.
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts.warning=false")
# Match local DPI behavior in frozen Windows builds.
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox
from sqlalchemy.exc import SQLAlchemyError

from app.auth.session import current_session
from app.branding import app_icon, configure_windows_app_id
from app.db.database import init_db
from app.db.repository import has_admin_recovery_key
from app.dialogs.change_password_dialog import ChangePasswordDialog
from app.dialogs.license_dialog import ensure_license_or_exit
from app.dialogs.login_dialog import LoginDialog
from app.dialogs.recovery_key_dialog import RecoveryKeyDialog
from app.licensing import get_license_status
from app.main_window import MainWindow
from app.styles import build_stylesheet
from app.support_identity import ensure_install_id


def main():
    # Before QApplication: otherwise Windows keeps the python.exe taskbar icon.
    configure_windows_app_id()

    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(build_stylesheet())
    app.setApplicationName("NGO Fundraising")
    app.setOrganizationName("MayleSoft")
    app.setApplicationDisplayName("NGO Fundraising")
    icon = app_icon()
    app.setWindowIcon(icon)
    # Keep False only while a session can return to login; always quit() explicitly.
    app.setQuitOnLastWindowClosed(False)

    # Windows needs a timer tick so Ctrl+C can reach the Qt loop.
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    _sigint_timer = QTimer()
    _sigint_timer.start(200)
    _sigint_timer.timeout.connect(lambda: None)

    try:
        init_db()
        ensure_install_id()
    except (SQLAlchemyError, OSError) as exc:
        QMessageBox.critical(
            None,
            "Startup error",
            f"Could not initialize the database:\n{exc}",
        )
        return 1

    if not ensure_license_or_exit(app):
        return 1

    state = {"window": None, "login": None}

    def shutdown():
        login = state.get("login")
        if login is not None:
            try:
                login.shutdown()
            except Exception:
                pass
            state["login"] = None
        state["window"] = None
        app.quit()

    def start_login():
        # Avoid stacking dialogs if one is already open.
        if state.get("login") is not None:
            return

        if not get_license_status().valid:
            if not ensure_license_or_exit(app):
                shutdown()
                return

        login = LoginDialog()
        state["login"] = login
        result = login.exec()
        state["login"] = None
        try:
            login.shutdown()
        except Exception:
            pass

        if result != LoginDialog.DialogCode.Accepted:
            shutdown()
            return

        user = getattr(login, "user", None)
        if user is not None and getattr(user, "must_change_password", False):
            change = ChangePasswordDialog(user.id, forced=True)
            if change.exec() != ChangePasswordDialog.DialogCode.Accepted:
                current_session.clear()
                QTimer.singleShot(0, start_login)
                return

        # Admin must register Install ID + recovery key with MayleSoft support.
        if (
            user is not None
            and getattr(user, "role", "") == "admin"
            and not has_admin_recovery_key()
        ):
            while True:
                recovery = RecoveryKeyDialog()
                if recovery.exec() == RecoveryKeyDialog.DialogCode.Accepted:
                    break
                if (
                    QMessageBox.question(
                        None,
                        "Support registration required",
                        "Password recovery will not work until this install is "
                        "registered with MayleSoft.\n\nRegister now?",
                    )
                    != QMessageBox.StandardButton.Yes
                ):
                    break

        window = MainWindow()
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        state["window"] = window

        def on_session_ended(to_login: bool):
            state["window"] = None
            if to_login:
                QTimer.singleShot(0, start_login)
            else:
                shutdown()

        window.session_ended.connect(on_session_ended)
        window.show()

    # Start login AFTER the event loop is running (fixes hang on first close).
    QTimer.singleShot(0, start_login)
    code = app.exec()
    return code


if __name__ == "__main__":
    sys.exit(main())
