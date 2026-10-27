from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget


class IconBadge(QWidget):
    """Circular icon badge painted with a glyph/symbol."""

    def __init__(
        self,
        glyph: str,
        color: str = "#176B5B",
        size: int = 56,
        parent=None,
    ):
        super().__init__(parent)
        self._glyph = glyph
        self._color = QColor(color)
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        ring = QColor(self._color)
        ring.setAlpha(42)
        painter.setBrush(QBrush(ring))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self._size, self._size)

        painter.setBrush(QBrush(self._color))
        inset = max(4, self._size // 10)
        painter.drawEllipse(
            inset, inset, self._size - 2 * inset, self._size - 2 * inset
        )

        painter.setPen(QPen(QColor("#FFFFFF")))
        font = QFont("Segoe UI Emoji", max(11, int(self._size * 0.38)))
        if not font.exactMatch():
            font = QFont("Segoe UI Symbol", max(11, int(self._size * 0.38)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._glyph)
        painter.end()
