from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.widgets.hover_frame import HoverFrame

ACCENTS = {
    "teal": "cardAccentTeal",
    "blue": "cardAccentBlue",
    "amber": "cardAccentAmber",
    "rose": "cardAccentRose",
    "violet": "cardAccentViolet",
}


class StatCard(HoverFrame):
    """Colored summary card with animated hover raise."""

    clicked = Signal()

    def __init__(
        self,
        title: str,
        value: str,
        detail: str = "",
        accent: str = "teal",
        *,
        clickable: bool = False,
    ):
        super().__init__(ACCENTS.get(accent, "cardAccentTeal"))
        self.setMinimumHeight(112)
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("cardValue")

        self.detail_label = QLabel(detail)
        self.detail_label.setObjectName("muted")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)

    def set_value(self, value: str, detail: str | None = None):
        self.value_label.setText(str(value))
        if detail is not None:
            self.detail_label.setText(detail)

    def mouseReleaseEvent(self, event):
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)
