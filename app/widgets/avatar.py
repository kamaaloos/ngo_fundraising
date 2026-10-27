from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QBrush, QFont
from PySide6.QtWidgets import QWidget


AVATAR_COLORS = (
    "#176B5B",
    "#2B6CB0",
    "#6B46C1",
    "#C05621",
    "#C53030",
    "#0F766E",
    "#1D4ED8",
    "#7C3AED",
)


def initials_for(name: str) -> str:
    parts = [p for p in (name or "").strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def color_for(name: str) -> str:
    seed = sum(ord(c) for c in (name or "x"))
    return AVATAR_COLORS[seed % len(AVATAR_COLORS)]


class AvatarWidget(QWidget):
    """Circular placeholder avatar with donor initials."""

    def __init__(self, name: str = "", size: int = 44, parent=None):
        super().__init__(parent)
        self._name = name or ""
        self._size = size
        self.setFixedSize(size, size)

    def set_name(self, name: str):
        self._name = name or ""
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(color_for(self._name))
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self._size, self._size)

        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", max(10, self._size // 3))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            initials_for(self._name),
        )
        painter.end()
