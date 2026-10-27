from PySide6.QtCore import QEasingCurve, QEvent, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect


class HoverFrame(QFrame):
    """Panel with soft animated shadow hover."""

    def __init__(self, object_name: str = "panel", parent=None):
        super().__init__(parent)
        self.setObjectName(object_name)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._apply_rest()
        self.setGraphicsEffect(self._shadow)

        self._pulse = QTimer(self)
        self._pulse.setInterval(16)
        self._pulse.timeout.connect(self._tick)
        self._blur_from = 14.0
        self._blur_to = 14.0
        self._y_from = 3.0
        self._y_to = 3.0
        self._step = 0
        self._steps = 10

    def _apply_rest(self):
        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 3)
        self._shadow.setColor(QColor(18, 35, 58, 38))

    def _apply_hover(self):
        self._shadow.setBlurRadius(28)
        self._shadow.setOffset(0, 10)
        self._shadow.setColor(QColor(18, 35, 58, 72))

    def _animate_to(self, blur: float, y: float, color: QColor):
        self._blur_from = float(self._shadow.blurRadius())
        self._y_from = float(self._shadow.yOffset())
        self._blur_to = blur
        self._y_to = y
        self._target_color = color
        self._step = 0
        self._steps = 10
        self._pulse.start()

    def _tick(self):
        self._step += 1
        t = min(1.0, self._step / self._steps)
        # Ease out
        t = 1 - (1 - t) * (1 - t)
        blur = self._blur_from + (self._blur_to - self._blur_from) * t
        y = self._y_from + (self._y_to - self._y_from) * t
        self._shadow.setBlurRadius(blur)
        self._shadow.setOffset(0, y)
        if hasattr(self, "_target_color"):
            self._shadow.setColor(self._target_color)
        if self._step >= self._steps:
            self._pulse.stop()

    def enterEvent(self, event: QEvent):
        self._animate_to(28, 10, QColor(18, 35, 58, 72))
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self._animate_to(14, 3, QColor(18, 35, 58, 38))
        super().leaveEvent(event)
