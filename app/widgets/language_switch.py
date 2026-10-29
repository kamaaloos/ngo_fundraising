"""Compact EN / ع / SO language toggle (matches the landing site)."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from app.i18n import LANGUAGE_OPTIONS, get_language, normalize_language


class LanguageSwitch(QWidget):
    """Three-button language picker. Emits language code when the user picks one."""

    language_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("languageSwitch")
        self._updating = False

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        shorts = {"en": "EN", "ar": "ع", "so": "SO"}
        for code, label in LANGUAGE_OPTIONS:
            btn = QPushButton(shorts.get(code, code.upper()))
            btn.setObjectName("langSwitchBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(label)
            btn.setMinimumHeight(32)
            btn.setMinimumWidth(44)
            btn.setProperty("lang_code", code)
            self._group.addButton(btn)
            self._buttons[code] = btn
            row.addWidget(btn)
            btn.toggled.connect(self._on_toggled)

        row.addStretch(1)
        self.set_language(get_language())

    def set_language(self, code: str) -> None:
        code = normalize_language(code)
        self._updating = True
        btn = self._buttons.get(code)
        if btn is not None:
            btn.setChecked(True)
        self._updating = False

    def current_language(self) -> str:
        for code, btn in self._buttons.items():
            if btn.isChecked():
                return code
        return "en"

    def _on_toggled(self, checked: bool) -> None:
        if self._updating or not checked:
            return
        sender = self.sender()
        if sender is None:
            return
        code = normalize_language(str(sender.property("lang_code") or "en"))
        self.language_changed.emit(code)
