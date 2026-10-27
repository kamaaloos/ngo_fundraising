"""Appearance settings: theme color, day/night, organization logo."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from app.settings_store import (
    MODES,
    THEME_PRESETS,
    clear_user_logo,
    load_settings,
    save_settings,
    set_user_logo,
    user_logo_path,
)


class SettingsPage(QWidget):
    """User appearance preferences (does not change the MayleSoft app icon)."""

    appearance_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("contentArea")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        note = QLabel(
            "Personalize this computer’s look. Your organization logo appears in "
            "the sidebar — the MayleSoft app icon stays unchanged."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        # ---- Theme color ----
        theme_card = QFrame()
        theme_card.setObjectName("panel")
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.setContentsMargins(18, 16, 18, 16)
        theme_heading = QLabel("Theme color")
        theme_heading.setObjectName("sectionTitle")
        theme_layout.addWidget(theme_heading)
        theme_hint = QLabel("Accent color for buttons, highlights, and navigation.")
        theme_hint.setObjectName("muted")
        theme_layout.addWidget(theme_hint)

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
        mode_card = QFrame()
        mode_card.setObjectName("panel")
        mode_layout = QVBoxLayout(mode_card)
        mode_layout.setContentsMargins(18, 16, 18, 16)
        mode_heading = QLabel("Display mode")
        mode_heading.setObjectName("sectionTitle")
        mode_layout.addWidget(mode_heading)
        mode_hint = QLabel("Day keeps a light workspace; Night uses a dark workspace.")
        mode_hint.setObjectName("muted")
        mode_layout.addWidget(mode_hint)

        self.mode_group = QButtonGroup(self)
        mode_row = QHBoxLayout()
        for key, label in MODES.items():
            btn = QRadioButton(label)
            btn.setProperty("mode_key", key)
            self.mode_group.addButton(btn)
            mode_row.addWidget(btn)
            btn.toggled.connect(self._on_mode_toggled)
        mode_row.addStretch()
        mode_layout.addLayout(mode_row)
        layout.addWidget(mode_card)

        # ---- User / org logo ----
        logo_card = QFrame()
        logo_card.setObjectName("panel")
        logo_layout = QVBoxLayout(logo_card)
        logo_layout.setContentsMargins(18, 16, 18, 16)
        logo_heading = QLabel("Organization logo")
        logo_heading.setObjectName("sectionTitle")
        logo_layout.addWidget(logo_heading)
        logo_hint = QLabel(
            "Shown in the sidebar under your session. This is your logo — "
            "not the NGO Fundraising app icon."
        )
        logo_hint.setObjectName("muted")
        logo_hint.setWordWrap(True)
        logo_layout.addWidget(logo_hint)

        preview_row = QHBoxLayout()
        self.logo_preview = QLabel("No organization logo")
        self.logo_preview.setObjectName("muted")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setMinimumSize(160, 100)
        self.logo_preview.setStyleSheet(
            "border: 1px dashed #C5D0DE; border-radius: 10px; padding: 8px;"
        )
        preview_row.addWidget(self.logo_preview)

        logo_actions = QVBoxLayout()
        choose = QPushButton("Choose logo…")
        choose.setObjectName("primaryButton")
        choose.clicked.connect(self._choose_logo)
        remove = QPushButton("Remove logo")
        remove.setObjectName("ghostButton")
        remove.clicked.connect(self._remove_logo)
        logo_actions.addWidget(choose)
        logo_actions.addWidget(remove)
        logo_actions.addStretch()
        preview_row.addLayout(logo_actions)
        preview_row.addStretch()
        logo_layout.addLayout(preview_row)
        layout.addWidget(logo_card)

        # ---- About / install ----
        about = QFrame()
        about.setObjectName("panel")
        about_layout = QFormLayout(about)
        about_layout.setContentsMargins(18, 16, 18, 16)
        about_title = QLabel("About")
        about_title.setObjectName("sectionTitle")
        about_layout.addRow(about_title)
        from app.branding import COPYRIGHT_TEXT
        from app.support_identity import SUPPORT_EMAIL, get_install_id

        about_layout.addRow("Product", QLabel(COPYRIGHT_TEXT))
        about_layout.addRow("Support email", QLabel(SUPPORT_EMAIL))
        install = QLabel(get_install_id())
        install.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        about_layout.addRow("Install ID", install)
        layout.addWidget(about)

        layout.addStretch(1)
        self.refresh()

    def refresh(self):
        settings = load_settings()
        for btn in self.theme_group.buttons():
            btn.blockSignals(True)
            btn.setChecked(btn.property("theme_key") == settings.accent_key())
            btn.blockSignals(False)
        for btn in self.mode_group.buttons():
            btn.blockSignals(True)
            btn.setChecked(btn.property("mode_key") == settings.mode_key())
            btn.blockSignals(False)
        self._refresh_logo_preview()

    def _refresh_logo_preview(self):
        path = user_logo_path()
        if path is None:
            self.logo_preview.setPixmap(QPixmap())
            self.logo_preview.setText("No organization logo")
            return
        pix = QPixmap(str(path))
        if pix.isNull():
            self.logo_preview.setText("Could not load logo")
            return
        self.logo_preview.setText("")
        self.logo_preview.setPixmap(
            pix.scaled(
                150,
                90,
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
        settings.has_user_logo = user_logo_path() is not None
        save_settings(settings)
        self.appearance_changed.emit()

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
