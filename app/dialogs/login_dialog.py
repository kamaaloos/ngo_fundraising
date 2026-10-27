from pathlib import Path

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QTimer,
    Qt,
)
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import current_session
from app.branding import app_icon, apply_windows_titlebar_theme, copyright_label, logo_label
from app.settings_store import THEME_PRESETS, load_settings
from app.db.repository import (
    authenticate,
    has_admin_recovery_key,
    reset_local_admin_password,
)
from app.db.seed import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME
from app.licensing import get_license_status
from app.support_identity import SUPPORT_CONTACT, SUPPORT_EMAIL, get_install_id
from app.widgets.password_edit import IconLineEdit

HERO_PATH = Path(__file__).resolve().parent.parent / "assets" / "login_hero.jpg"

# Rotating marketing copy on the login hero (tagline, caption).
HERO_SLIDES = (
    (
        "Sadaqah with clarity.\nEvery gift accounted.",
        "Islamic fundraising · Projects · Donors · Reports",
    ),
    (
        "Trust earned in every\npledge and payment.",
        "Collect · Track · Report — with full transparency",
    ),
    (
        "From donor to impact,\nclearly recorded.",
        "MayleSoft NGO-fund · Built for community care",
    ),
    (
        "Raise more. Spend wisely.\nKnow the difference.",
        "Pledged · Raised · Outstanding · Expenses",
    ),
    (
        "One place for every\ncampaign and collector.",
        "Staff access · Project boards · Live charts",
    ),
)


class HeroPanel(QWidget):
    """Left cinematic panel: Ken Burns zoom/pan + light sweep."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("loginHero")
        self.setMinimumWidth(380)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._pixmap = QPixmap(str(HERO_PATH)) if HERO_PATH.exists() else QPixmap()

        self._zoom = 1.08
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._veil = 0.55
        self._sweep = -0.2
        self._text_opacity = 0.0
        self._slide_index = 0
        self._swap_busy = False

        overlay = QVBoxLayout(self)
        overlay.setContentsMargins(40, 48, 40, 48)
        overlay.addStretch(3)

        self.brand = logo_label(220, 160, object_name="loginHeroLogo")
        overlay.addWidget(self.brand, 0, Qt.AlignmentFlag.AlignLeft)

        first_tagline, first_caption = HERO_SLIDES[0]
        self.tagline = QLabel(first_tagline)
        self.tagline.setObjectName("loginHeroTagline")
        self.tagline.setWordWrap(True)
        self.tagline.setMinimumHeight(86)
        overlay.addWidget(self.tagline)

        self.caption = QLabel(first_caption)
        self.caption.setObjectName("loginHeroCaption")
        self.caption.setWordWrap(True)
        self.caption.setMinimumHeight(36)
        overlay.addWidget(self.caption)
        overlay.addStretch(1)

        self.hero_copyright = copyright_label(object_name="loginHeroCopyright")
        self.hero_copyright.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
        )
        overlay.addWidget(self.hero_copyright)

        for label in (self.brand, self.tagline, self.caption, self.hero_copyright):
            fx = QGraphicsOpacityEffect(label)
            fx.setOpacity(0.0)
            label.setGraphicsEffect(fx)
            label._fx = fx  # noqa: SLF001

        self._kenburns = QTimer(self)
        self._kenburns.setInterval(32)
        self._kenburns.timeout.connect(self._tick_cinematic)

        self._slogan_timer = QTimer(self)
        self._slogan_timer.setInterval(4200)
        self._slogan_timer.timeout.connect(self._swap_slogan)

    def get_zoom(self):
        return self._zoom

    def set_zoom(self, value):
        self._zoom = float(value)
        self.update()

    zoom = Property(float, get_zoom, set_zoom)

    def get_pan_x(self):
        return self._pan_x

    def set_pan_x(self, value):
        self._pan_x = float(value)
        self.update()

    pan_x = Property(float, get_pan_x, set_pan_x)

    def get_pan_y(self):
        return self._pan_y

    def set_pan_y(self, value):
        self._pan_y = float(value)
        self.update()

    pan_y = Property(float, get_pan_y, set_pan_y)

    def get_sweep(self):
        return self._sweep

    def set_sweep(self, value):
        self._sweep = float(value)
        self.update()

    sweep = Property(float, get_sweep, set_sweep)

    def stop_cinematic(self):
        self._kenburns.stop()
        self._slogan_timer.stop()
        intro = getattr(self, "_intro_group", None)
        if intro is not None:
            intro.stop()
        swap = getattr(self, "_swap_group", None)
        if swap is not None:
            swap.stop()

    def start_cinematic(self):
        # Continuous slow Ken Burns
        self._zoom = 1.12
        self._pan_x = -0.04
        self._pan_y = 0.02
        self._kenburns.start()

        # Intro zoom settle
        zoom_in = QPropertyAnimation(self, b"zoom")
        zoom_in.setDuration(2200)
        zoom_in.setStartValue(1.22)
        zoom_in.setEndValue(1.08)
        zoom_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        pan = QPropertyAnimation(self, b"pan_x")
        pan.setDuration(2200)
        pan.setStartValue(-0.08)
        pan.setEndValue(0.02)
        pan.setEasingCurve(QEasingCurve.Type.InOutSine)

        sweep = QPropertyAnimation(self, b"sweep")
        sweep.setDuration(1600)
        sweep.setStartValue(-0.35)
        sweep.setEndValue(1.25)
        sweep.setEasingCurve(QEasingCurve.Type.InOutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(zoom_in)
        group.addAnimation(pan)
        group.addAnimation(sweep)
        self._intro_group = group
        group.start()

        # Fade text in after a beat, then start rotating slogans
        QTimer.singleShot(280, self._fade_text_in)

    def _fade_text_in(self):
        for i, label in enumerate(
            (self.brand, self.tagline, self.caption, self.hero_copyright)
        ):
            anim = QPropertyAnimation(label._fx, b"opacity", self)
            anim.setDuration(700)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            setattr(self, f"_text_anim_{i}", anim)
            QTimer.singleShot(i * 140, anim.start)
        # Start swapping after the first slide has been readable for a while.
        QTimer.singleShot(3200, self._slogan_timer.start)

    def _swap_slogan(self):
        if self._swap_busy or not HERO_SLIDES:
            return
        self._swap_busy = True
        self._slide_index = (self._slide_index + 1) % len(HERO_SLIDES)
        next_tagline, next_caption = HERO_SLIDES[self._slide_index]

        fade_out = QParallelAnimationGroup(self)
        for label in (self.tagline, self.caption):
            anim = QPropertyAnimation(label._fx, b"opacity", self)
            anim.setDuration(380)
            anim.setStartValue(float(label._fx.opacity()))
            anim.setEndValue(0.0)
            anim.setEasingCurve(QEasingCurve.Type.InCubic)
            fade_out.addAnimation(anim)

        def apply_next():
            self.tagline.setText(next_tagline)
            self.caption.setText(next_caption)
            fade_in = QParallelAnimationGroup(self)
            for label in (self.tagline, self.caption):
                anim = QPropertyAnimation(label._fx, b"opacity", self)
                anim.setDuration(520)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                fade_in.addAnimation(anim)

            def done():
                self._swap_busy = False

            fade_in.finished.connect(done)
            self._swap_group = fade_in
            fade_in.start()

        fade_out.finished.connect(apply_next)
        self._swap_group = fade_out
        fade_out.start()

    def _tick_cinematic(self):
        # Gentle ongoing drift after intro
        self._pan_x += 0.00035
        self._pan_y -= 0.00012
        if self._pan_x > 0.06:
            self._pan_x = -0.05
        if self._pan_y < -0.04:
            self._pan_y = 0.03
        self._zoom = 1.08 + 0.02 * abs((self._pan_x + 0.05) / 0.11)
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        if not self._pixmap.isNull():
            zoom = max(1.05, self._zoom)
            target_w = int(rect.width() * zoom)
            target_h = int(rect.height() * zoom)
            scaled = self._pixmap.scaled(
                target_w,
                target_h,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            max_x = max(0, scaled.width() - rect.width())
            max_y = max(0, scaled.height() - rect.height())
            x = int((0.5 + self._pan_x) * max_x)
            y = int((0.5 + self._pan_y) * max_y)
            x = min(max(0, x), max_x)
            y = min(max(0, y), max_y)
            painter.drawPixmap(
                rect, scaled, QRect(x, y, rect.width(), rect.height())
            )
        else:
            painter.fillRect(rect, QColor("#12304A"))

        # Dark cinematic veil
        painter.fillRect(rect, QColor(8, 18, 30, 110))
        painter.fillRect(
            0,
            int(rect.height() * 0.42),
            rect.width(),
            int(rect.height() * 0.58),
            QColor(8, 18, 30, 160),
        )

        # Light sweep band
        sweep_x = int(self._sweep * rect.width())
        band_w = max(80, int(rect.width() * 0.18))
        painter.fillRect(
            sweep_x - band_w // 2,
            0,
            band_w,
            rect.height(),
            QColor(255, 255, 255, 28),
        )
        painter.end()


class LoginFormCard(QFrame):
    """Right-side form with primary border (no nested graphics effect)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("loginFormCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def enterEvent(self, event):
        self.setProperty("raised", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setProperty("raised", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in — NGO Fundraising")
        self.setWindowIcon(app_icon())
        self._titlebar_themed = False
        self.setModal(True)
        self.setMinimumSize(980, 620)
        self.resize(1100, 700)
        self.setObjectName("loginDialog")
        self.user = None

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.hero = HeroPanel()
        root.addWidget(self.hero, 5)

        right = QWidget()
        right.setObjectName("loginRightPane")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(48, 40, 48, 40)
        right_layout.addStretch(1)

        self.form_card = LoginFormCard()
        form_layout = QVBoxLayout(self.form_card)
        form_layout.setContentsMargins(36, 34, 36, 32)
        form_layout.setSpacing(14)

        form_logo = logo_label(150, 110, object_name="loginFormLogo")
        form_layout.addWidget(form_logo, 0, Qt.AlignmentFlag.AlignLeft)

        eyebrow = QLabel("SECURE ACCESS")
        eyebrow.setObjectName("loginEyebrow")
        form_layout.addWidget(eyebrow)

        title = QLabel("Welcome back")
        title.setObjectName("loginTitle")
        form_layout.addWidget(title)

        subtitle = QLabel(
            "Sign in to manage Islamic fundraising projects, donors, and reports."
        )
        subtitle.setObjectName("loginSubtitle")
        subtitle.setWordWrap(True)
        form_layout.addWidget(subtitle)
        form_layout.addSpacing(10)

        user_label = QLabel("Username")
        user_label.setObjectName("loginFieldLabel")
        form_layout.addWidget(user_label)
        self.username = IconLineEdit("Enter your username", leading="👤")
        form_layout.addWidget(self.username)

        pass_label = QLabel("Password")
        pass_label.setObjectName("loginFieldLabel")
        form_layout.addWidget(pass_label)
        self.password = IconLineEdit("Enter your password", leading="🔒", password=True)
        form_layout.addWidget(self.password)

        form_layout.addSpacing(8)
        login_btn = QPushButton("Sign in")
        login_btn.setObjectName("loginPrimary")
        login_btn.setMinimumHeight(48)
        login_btn.clicked.connect(self._try_login)
        form_layout.addWidget(login_btn)

        hint = QLabel(
            "First launch creates admin — you will be asked to change the password."
        )
        hint.setObjectName("loginHint")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(hint)

        forgot = QPushButton("Forgot admin password? Contact support")
        forgot.setObjectName("loginForgotLink")
        forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot.setFlat(True)
        forgot.clicked.connect(self._reset_admin_password)
        form_layout.addWidget(forgot, 0, Qt.AlignmentFlag.AlignCenter)

        license_link = QPushButton("Enter / renew license code")
        license_link.setObjectName("loginForgotLink")
        license_link.setCursor(Qt.CursorShape.PointingHandCursor)
        license_link.setFlat(True)
        license_link.clicked.connect(self._enter_license)
        form_layout.addWidget(license_link, 0, Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(self.form_card)
        right_layout.addSpacing(16)
        right_layout.addWidget(copyright_label(object_name="loginCopyright"))
        self.install_label = QLabel(f"Install ID: {get_install_id()}")
        self.install_label.setObjectName("loginInstallId")
        self.install_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.install_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        right_layout.addWidget(self.install_label)
        self.license_label = QLabel("")
        self.license_label.setObjectName("loginInstallId")
        self.license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.license_label.setWordWrap(True)
        right_layout.addWidget(self.license_label)
        self._refresh_license_label()
        right_layout.addStretch(1)
        root.addWidget(right, 4)

        self.password.edit.returnPressed.connect(self._try_login)
        self.username.edit.returnPressed.connect(lambda: self.password.setFocus())

        self.setWindowOpacity(0.0)
        self.hero.setMaximumWidth(0)
        QTimer.singleShot(50, self._play_cinematic)

    def _play_cinematic(self):
        target_hero = max(460, int(self.width() * 0.56))

        fade = QPropertyAnimation(self, b"windowOpacity", self)
        fade.setDuration(650)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Very visible left reveal
        reveal = QPropertyAnimation(self.hero, b"maximumWidth", self)
        reveal.setDuration(1100)
        reveal.setStartValue(0)
        reveal.setEndValue(target_hero)
        reveal.setEasingCurve(QEasingCurve.Type.OutBack)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade)
        group.addAnimation(reveal)

        def finish():
            self.hero.setMaximumWidth(16777215)
            self.hero.start_cinematic()

        group.finished.connect(finish)
        self._intro = group
        group.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.hero.update()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._titlebar_themed:
            self._titlebar_themed = True
            settings = load_settings()
            apply_windows_titlebar_theme(
                self,
                dark=settings.mode_key() == "night",
                caption_hex=THEME_PRESETS[settings.accent_key()]["accent"],
            )

    def shutdown(self):
        """Stop timers/animations so the process can exit cleanly."""
        try:
            self.hero.stop_cinematic()
        except Exception:
            pass

    def closeEvent(self, event):
        self.shutdown()
        super().closeEvent(event)

    def reject(self):
        self.shutdown()
        super().reject()

    def accept(self):
        self.shutdown()
        super().accept()

    def _refresh_license_label(self):
        status = get_license_status()
        if status.expires_on is None:
            self.license_label.setText("License: not set")
        elif status.valid:
            self.license_label.setText(
                f"License until {status.expires_on.isoformat()} "
                f"({status.days_remaining} day(s) left)"
            )
        else:
            self.license_label.setText(
                f"License expired {status.expires_on.isoformat()} — contact support"
            )

    def _enter_license(self):
        from app.dialogs.license_dialog import LicenseDialog

        dialog = LicenseDialog(self, blocking=False)
        dialog.exec()
        self._refresh_license_label()

    def _reset_admin_password(self):
        install_id = get_install_id()
        if not has_admin_recovery_key():
            QMessageBox.information(
                self,
                "Contact support",
                "This installation is not registered for password recovery yet.\n\n"
                f"Email {SUPPORT_EMAIL} and quote Install ID:\n{install_id}\n\n"
                f"({SUPPORT_CONTACT})",
            )
            return

        guide = QMessageBox(self)
        guide.setIcon(QMessageBox.Icon.Information)
        guide.setWindowTitle("Contact support")
        guide.setText(
            f"Email {SUPPORT_EMAIL} and quote your Install ID:\n\n{install_id}"
        )
        guide.setInformativeText(
            f"({SUPPORT_CONTACT})\n\n"
            "Support will look up your recovery key and tell you what to enter next.\n"
            "Only continue below when support has given you the recovery key."
        )
        guide.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        guide.button(QMessageBox.StandardButton.Ok).setText("I have the recovery key")
        if guide.exec() != QMessageBox.StandardButton.Ok:
            return

        key, ok = QInputDialog.getText(
            self,
            "Enter recovery key from support",
            "Recovery key (from your software provider):",
            echo=QLineEdit.EchoMode.Password,
        )
        if not ok:
            return
        if not (key or "").strip():
            QMessageBox.warning(self, "Reset", "Recovery key is required.")
            return

        try:
            username, temp = reset_local_admin_password(
                temporary_password=DEFAULT_ADMIN_PASSWORD,
                username=DEFAULT_ADMIN_USERNAME,
                recovery_key=key,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Reset failed", str(exc))
            return

        self.username.setText(username)
        self.password.setText(temp)
        QMessageBox.information(
            self,
            "Password reset",
            f'Admin "{username}" was reset on this computer.\n\n'
            f"Temporary password: {temp}\n"
            "Sign in now, then set a new password when prompted.",
        )

    def _try_login(self):
        username = self.username.text().strip()
        password = self.password.text()
        if not username or not password:
            QMessageBox.warning(self, "Sign in", "Enter username and password.")
            return

        user = authenticate(username, password)
        if user is None:
            QMessageBox.warning(
                self, "Sign in failed", "Invalid credentials or inactive account."
            )
            return

        current_session.user_id = user.id
        current_session.username = user.username
        current_session.full_name = user.full_name or user.username
        current_session.role = user.role
        current_session.project_ids = [p.id for p in user.projects]
        current_session.current_project_id = None
        self.user = user
        self.accept()
