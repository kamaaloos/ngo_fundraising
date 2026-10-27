from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Signal,
)
from PySide6.QtWidgets import QFrame, QStackedWidget, QVBoxLayout


class FlipCard(QFrame):
    """Two-sided card with a horizontal flip-style animation (no graphics effects)."""

    flipped = Signal(bool)

    def __init__(self, front: QFrame, back: QFrame, width: int = 440, parent=None):
        super().__init__(parent)
        self.setObjectName("flipCardShell")
        self._card_width = width
        self._showing_back = False
        self._busy = False
        self.setFixedWidth(width)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.front = front
        self.back = back
        self.stack.addWidget(front)
        self.stack.addWidget(back)
        layout.addWidget(self.stack)

    @property
    def showing_back(self) -> bool:
        return self._showing_back

    def flip(self):
        if self._busy:
            return
        self._busy = True
        to_back = not self._showing_back

        shrink_min = QPropertyAnimation(self, b"minimumWidth")
        shrink_min.setDuration(160)
        shrink_min.setStartValue(self._card_width)
        shrink_min.setEndValue(32)
        shrink_min.setEasingCurve(QEasingCurve.Type.InCubic)

        shrink_max = QPropertyAnimation(self, b"maximumWidth")
        shrink_max.setDuration(160)
        shrink_max.setStartValue(self._card_width)
        shrink_max.setEndValue(32)
        shrink_max.setEasingCurve(QEasingCurve.Type.InCubic)

        expand_min = QPropertyAnimation(self, b"minimumWidth")
        expand_min.setDuration(200)
        expand_min.setStartValue(32)
        expand_min.setEndValue(self._card_width)
        expand_min.setEasingCurve(QEasingCurve.Type.OutCubic)

        expand_max = QPropertyAnimation(self, b"maximumWidth")
        expand_max.setDuration(200)
        expand_max.setStartValue(32)
        expand_max.setEndValue(self._card_width)
        expand_max.setEasingCurve(QEasingCurve.Type.OutCubic)

        def swap():
            self._showing_back = to_back
            self.stack.setCurrentIndex(1 if to_back else 0)
            self.flipped.emit(to_back)

        shrink_min.finished.connect(swap)

        first = QParallelAnimationGroup()
        first.addAnimation(shrink_min)
        first.addAnimation(shrink_max)

        second = QParallelAnimationGroup()
        second.addAnimation(expand_min)
        second.addAnimation(expand_max)

        seq = QSequentialAnimationGroup(self)
        seq.addAnimation(first)
        seq.addAnimation(second)

        def done():
            self.setFixedWidth(self._card_width)
            self._busy = False

        seq.finished.connect(done)
        self._anim = seq
        seq.start()
