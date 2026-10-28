"""Appearance settings: language, theme, day/night, organization logo, backups."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import current_session
from app.db.database import (
    APP_DIR,
    DATABASE_PATH,
    export_database_backup,
    restore_database_backup,
)
from app.i18n import LANGUAGE_OPTIONS, restart_application, tr
from app.settings_store import (
    THEME_PRESETS,
    clear_user_logo,
    load_settings,
    save_settings,
    set_user_logo,
    user_logo_path,
)


def _panel() -> QFrame:
    card = QFrame()
    card.setObjectName("panel")
    card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    return card


def _wrap_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("muted")
    label.setWordWrap(True)
    label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
    return label


class SettingsPage(QWidget):
    """User appearance preferences (does not change the MayleSoft app icon)."""

    appearance_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("contentArea")
        self._updating_language = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        outer.addWidget(scroll)

        host = QWidget()
        host.setObjectName("contentArea")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        self.title_label = QLabel(tr("settings.title"))
        self.title_label.setObjectName("pageTitle")
        layout.addWidget(self.title_label)

        self.note_label = _wrap_label(tr("settings.note"))
        layout.addWidget(self.note_label)

        # ---- Language ----
        lang_card = _panel()
        lang_layout = QVBoxLayout(lang_card)
        lang_layout.setContentsMargins(18, 16, 18, 16)
        lang_layout.setSpacing(10)
        self.lang_heading = QLabel(tr("settings.language"))
        self.lang_heading.setObjectName("sectionTitle")
        lang_layout.addWidget(self.lang_heading)
        self.lang_hint = _wrap_label(tr("settings.language_hint"))
        lang_layout.addWidget(self.lang_hint)

        self.language_combo = QComboBox()
        self.language_combo.setMinimumHeight(36)
        self.language_combo.setMaximumWidth(280)
        for code, label in LANGUAGE_OPTIONS:
            self.language_combo.addItem(label, code)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self.language_combo)
        layout.addWidget(lang_card)

        # ---- Theme color ----
        theme_card = _panel()
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.setContentsMargins(18, 16, 18, 16)
        theme_layout.setSpacing(10)
        self.theme_heading = QLabel(tr("settings.theme"))
        self.theme_heading.setObjectName("sectionTitle")
        theme_layout.addWidget(self.theme_heading)
        self.theme_hint = _wrap_label(tr("settings.theme_hint"))
        theme_layout.addWidget(self.theme_hint)

        self.theme_group = QButtonGroup(self)
        theme_row = QHBoxLayout()
        theme_row.setSpacing(10)
        for key, preset in THEME_PRESETS.items():
            btn = QRadioButton(preset["label"])
            btn.setProperty("theme_key", key)
            swatch = QLabel("  ")
            swatch.setFixedSize(18, 18)
            swatch.setStyleSheet(
                f"background:{preset['accent']}; border-radius:4px; border:1px solid #00000033;"
            )
            cell = QHBoxLayout()
            cell.setSpacing(6)
            cell.addWidget(swatch)
            cell.addWidget(btn)
            wrap = QWidget()
            wrap.setLayout(cell)
            theme_row.addWidget(wrap)
            self.theme_group.addButton(btn)
            btn.toggled.connect(self._on_theme_toggled)
        theme_row.addStretch()
        theme_layout.addLayout(theme_row)
        layout.addWidget(theme_card)

        # ---- Day / night ----
        mode_card = _panel()
        mode_layout = QVBoxLayout(mode_card)
        mode_layout.setContentsMargins(18, 16, 18, 16)
        mode_layout.setSpacing(10)
        self.mode_heading = QLabel(tr("settings.mode"))
        self.mode_heading.setObjectName("sectionTitle")
        mode_layout.addWidget(self.mode_heading)
        self.mode_hint = _wrap_label(tr("settings.mode_hint"))
        mode_layout.addWidget(self.mode_hint)

        self.mode_group = QButtonGroup(self)
        mode_row = QHBoxLayout()
        for key, label_key in (
            ("day", "settings.mode.day"),
            ("night", "settings.mode.night"),
        ):
            btn = QRadioButton(tr(label_key))
            btn.setProperty("mode_key", key)
            btn.setProperty("label_key", label_key)
            self.mode_group.addButton(btn)
            mode_row.addWidget(btn)
            btn.toggled.connect(self._on_mode_toggled)
        mode_row.addStretch()
        mode_layout.addLayout(mode_row)
        layout.addWidget(mode_card)

        # ---- User / org logo ----
        logo_card = _panel()
        logo_layout = QVBoxLayout(logo_card)
        logo_layout.setContentsMargins(18, 16, 18, 16)
        logo_layout.setSpacing(10)
        self.logo_heading = QLabel(tr("settings.logo"))
        self.logo_heading.setObjectName("sectionTitle")
        logo_layout.addWidget(self.logo_heading)
        self.logo_hint = _wrap_label(tr("settings.logo_hint"))
        logo_layout.addWidget(self.logo_hint)

        preview_row = QHBoxLayout()
        self.logo_preview = QLabel(tr("settings.logo_none"))
        self.logo_preview.setObjectName("muted")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setFixedSize(160, 100)
        self.logo_preview.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.logo_preview.setStyleSheet(
            "border: 1px dashed #C5D0DE; border-radius: 10px; padding: 8px;"
        )
        preview_row.addWidget(self.logo_preview)

        logo_actions = QVBoxLayout()
        self.choose_logo_btn = QPushButton(tr("settings.logo_choose"))
        self.choose_logo_btn.setObjectName("primaryButton")
        self.choose_logo_btn.clicked.connect(self._choose_logo)
        self.remove_logo_btn = QPushButton(tr("settings.logo_remove"))
        self.remove_logo_btn.setObjectName("ghostButton")
        self.remove_logo_btn.clicked.connect(self._remove_logo)
        logo_actions.addWidget(self.choose_logo_btn)
        logo_actions.addWidget(self.remove_logo_btn)
        logo_actions.addStretch()
        preview_row.addLayout(logo_actions)
        preview_row.addStretch()
        logo_layout.addLayout(preview_row)
        layout.addWidget(logo_card)

        # ---- Data backup (admin) ----
        backup_card = _panel()
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(18, 16, 18, 16)
        backup_layout.setSpacing(10)
        self.backup_heading = QLabel(tr("settings.backup"))
        self.backup_heading.setObjectName("sectionTitle")
        backup_layout.addWidget(self.backup_heading)
        self.backup_hint = _wrap_label(tr("settings.backup_hint"))
        backup_layout.addWidget(self.backup_hint)

        self.db_path_label = _wrap_label("")
        self.db_path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        backup_layout.addWidget(self.db_path_label)

        self.backup_on_exit_cb = QCheckBox(tr("settings.backup_on_exit"))
        self.backup_on_exit_cb.setMinimumHeight(28)
        self.backup_on_exit_cb.toggled.connect(self._on_backup_on_exit_toggled)
        backup_layout.addWidget(self.backup_on_exit_cb)

        backup_row = QHBoxLayout()
        self.export_backup_btn = QPushButton(tr("settings.export_backup"))
        self.export_backup_btn.setObjectName("primaryButton")
        self.export_backup_btn.clicked.connect(self._export_backup)
        self.restore_backup_btn = QPushButton(tr("settings.restore_backup"))
        self.restore_backup_btn.setObjectName("ghostButton")
        self.restore_backup_btn.clicked.connect(self._restore_backup)
        backup_row.addWidget(self.export_backup_btn)
        backup_row.addWidget(self.restore_backup_btn)
        backup_row.addStretch()
        backup_layout.addLayout(backup_row)
        layout.addWidget(backup_card)
        self.backup_card = backup_card

        # ---- About / install ----
        about = _panel()
        about_layout = QFormLayout(about)
        about_layout.setContentsMargins(18, 16, 18, 16)
        about_layout.setHorizontalSpacing(18)
        about_layout.setVerticalSpacing(10)
        self.about_title = QLabel(tr("settings.about"))
        self.about_title.setObjectName("sectionTitle")
        about_layout.addRow(self.about_title)
        from app.branding import COPYRIGHT_TEXT
        from app.support_identity import SUPPORT_EMAIL, get_install_id

        about_layout.addRow(tr("settings.product"), QLabel(COPYRIGHT_TEXT))
        about_layout.addRow(tr("settings.support_email"), QLabel(SUPPORT_EMAIL))
        install = QLabel(get_install_id())
        install.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        about_layout.addRow(tr("settings.install_id"), install)
        layout.addWidget(about)

        layout.addStretch(1)
        scroll.setWidget(host)
        self.refresh()

    def refresh(self):
        settings = load_settings()
        self._updating_language = True
        idx = self.language_combo.findData(settings.language_key())
        if idx < 0:
            idx = 0
        self.language_combo.setCurrentIndex(idx)
        self._updating_language = False

        for btn in self.theme_group.buttons():
            btn.blockSignals(True)
            btn.setChecked(btn.property("theme_key") == settings.accent_key())
            btn.blockSignals(False)
        for btn in self.mode_group.buttons():
            btn.blockSignals(True)
            label_key = btn.property("label_key")
            if label_key:
                btn.setText(tr(str(label_key)))
            btn.setChecked(btn.property("mode_key") == settings.mode_key())
            btn.blockSignals(False)
        self._refresh_logo_preview()
        is_admin = current_session.is_admin
        self.backup_card.setVisible(is_admin)
        self.db_path_label.setText(f"Database file: {DATABASE_PATH}")
        self.backup_on_exit_cb.blockSignals(True)
        self.backup_on_exit_cb.setChecked(settings.backup_on_exit)
        self.backup_on_exit_cb.blockSignals(False)

    def _refresh_logo_preview(self):
        path = user_logo_path()
        if path is None:
            self.logo_preview.setPixmap(QPixmap())
            self.logo_preview.setText(tr("settings.logo_none"))
            return
        pix = QPixmap(str(path))
        if pix.isNull():
            self.logo_preview.setText("Could not load logo")
            return
        self.logo_preview.setText("")
        self.logo_preview.setPixmap(
            pix.scaled(
                144,
                84,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _selected_theme(self) -> str:
        for btn in self.theme_group.buttons():
            if btn.isChecked():
                return str(btn.property("theme_key") or "teal")
        return "teal"

    def _selected_mode(self) -> str:
        for btn in self.mode_group.buttons():
            if btn.isChecked():
                return str(btn.property("mode_key") or "day")
        return "day"

    def _persist_and_emit(self):
        settings = load_settings()
        settings.theme = self._selected_theme()
        settings.mode = self._selected_mode()
        settings.language = str(
            self.language_combo.currentData() or settings.language_key()
        )
        settings.has_user_logo = user_logo_path() is not None
        save_settings(settings)
        self.appearance_changed.emit()

    def _on_language_changed(self, _index: int):
        if self._updating_language:
            return
        code = str(self.language_combo.currentData() or "en")
        settings = load_settings()
        if code == settings.language_key():
            return
        settings.language = code
        settings.theme = self._selected_theme()
        settings.mode = self._selected_mode()
        save_settings(settings)
        QMessageBox.information(
            self, tr("settings.language"), tr("settings.language_restart")
        )
        restart_application()

    def _on_theme_toggled(self, checked: bool):
        if checked:
            self._persist_and_emit()

    def _on_mode_toggled(self, checked: bool):
        if checked:
            self._persist_and_emit()

    def _choose_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose organization logo",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)",
        )
        if not path:
            return
        try:
            set_user_logo(path)
        except Exception as exc:
            QMessageBox.warning(self, "Logo", str(exc))
            return
        self._refresh_logo_preview()
        self.appearance_changed.emit()

    def _remove_logo(self):
        if user_logo_path() is None:
            return
        if (
            QMessageBox.question(self, "Remove logo", "Remove the organization logo?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        clear_user_logo()
        self._refresh_logo_preview()
        self.appearance_changed.emit()

    def _on_backup_on_exit_toggled(self, checked: bool):
        settings = load_settings()
        settings.backup_on_exit = bool(checked)
        save_settings(settings)

    def _export_backup(self):
        if not current_session.is_admin:
            QMessageBox.warning(self, "Backup", "Administrator access required.")
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suggested = str(Path.home() / "Documents" / f"NGO_Fundraising_backup_{stamp}.sqlite3")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export database backup",
            suggested,
            "SQLite database (*.sqlite3 *.db);;All files (*.*)",
        )
        if not path:
            return
        try:
            dest = export_database_backup(path)
        except Exception as exc:
            QMessageBox.critical(self, "Backup failed", str(exc))
            return
        QMessageBox.information(
            self,
            "Backup saved",
            f"Database copied to:\n{dest}\n\n"
            f"Local auto-backups (exit / upgrades) also stay under:\n{APP_DIR}",
        )

    def _restore_backup(self):
        if not current_session.is_admin:
            QMessageBox.warning(self, "Restore", "Administrator access required.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Restore database from backup",
            str(Path.home() / "Documents"),
            "SQLite database (*.sqlite3 *.db);;All files (*.*)",
        )
        if not path:
            return
        confirm = QMessageBox.warning(
            self,
            "Restore database?",
            "This replaces ALL data on this computer with the selected backup.\n\n"
            "A safety copy of the current database is kept first. "
            "The app will quit after restore — open it again to continue.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            safety = restore_database_backup(path)
        except Exception as exc:
            QMessageBox.critical(self, "Restore failed", str(exc))
            return
        QMessageBox.information(
            self,
            "Restore complete",
            f"Database restored.\n\nPrevious data saved as:\n{safety}\n\n"
            "The application will now quit. Start it again to use the restored data.",
        )
        QApplication.instance().quit()
