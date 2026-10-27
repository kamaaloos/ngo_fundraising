from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


class IconLineEdit(QWidget):
    """Bordered input with person/lock icon, eye toggle, and hover-rise shadow."""

    def __init__(
        self,
        placeholder: str = "",
        leading: str = "👤",
        password: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("loginInputShell")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setProperty("hovered", False)
        self.setProperty("focused", False)
        self.setMinimumHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 10, 8)
        layout.setSpacing(10)

        self.leading = QLabel(leading)
        self.leading.setObjectName("loginFieldIcon")
        self.leading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.leading.setFixedWidth(28)
        layout.addWidget(self.leading)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.setObjectName("loginInput")
        if password:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.edit, 1)

        self._password = password
        self._shown = False
        self.trailing = QPushButton("👁")
        self.trailing.setObjectName("loginEyeButton")
        self.trailing.setFlat(True)
        self.trailing.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.trailing.setCursor(Qt.CursorShape.PointingHandCursor)
        self.trailing.setFixedSize(34, 34)
        self.trailing.setVisible(password)
        if password:
            self.trailing.setToolTip("Show password")
            self.trailing.clicked.connect(self.toggle_password)
        layout.addWidget(self.trailing)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._apply_rest()
        self.setGraphicsEffect(self._shadow)

        self._blur_anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._blur_anim.setDuration(160)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._y_anim = QPropertyAnimation(self._shadow, b"yOffset", self)
        self._y_anim.setDuration(160)
        self._y_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.installEventFilter(self)
        self.edit.installEventFilter(self)

    def _apply_rest(self):
        self._shadow.setBlurRadius(0)
        self._shadow.setOffset(0, 0)
        self._shadow.setColor(QColor(23, 107, 91, 0))

    def _animate_shadow(self, blur: float, y: float, alpha: int):
        self._blur_anim.stop()
        self._y_anim.stop()
        self._blur_anim.setStartValue(self._shadow.blurRadius())
        self._blur_anim.setEndValue(blur)
        self._y_anim.setStartValue(self._shadow.yOffset())
        self._y_anim.setEndValue(y)
        self._shadow.setColor(QColor(23, 107, 91, alpha))
        self._blur_anim.start()
        self._y_anim.start()

    def text(self) -> str:
        return self.edit.text()

    def setText(self, value: str):
        self.edit.setText(value)

    def setFocus(self, reason=Qt.FocusReason.OtherFocusReason):
        self.edit.setFocus(reason)

    def toggle_password(self):
        if not self._password:
            return
        self._shown = not self._shown
        if self._shown:
            self.edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.trailing.setText("🔒")
            self.trailing.setToolTip("Hide password")
        else:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.trailing.setText("👁")
            self.trailing.setToolTip("Show password")

    def _refresh_state(self, hovered: bool | None = None, focused: bool | None = None):
        if hovered is not None:
            self.setProperty("hovered", hovered)
        if focused is not None:
            self.setProperty("focused", focused)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

        active = bool(self.property("hovered") or self.property("focused"))
        if active:
            self._animate_shadow(22, 8, 95)
        else:
            self._animate_shadow(0, 0, 0)

    def eventFilter(self, obj, event):
        et = event.type()
        if et == QEvent.Type.Enter:
            self._refresh_state(hovered=True)
        elif et == QEvent.Type.Leave:
            if not self.edit.hasFocus():
                self._refresh_state(hovered=False)
        elif et == QEvent.Type.FocusIn and obj is self.edit:
            self._refresh_state(hovered=True, focused=True)
        elif et == QEvent.Type.FocusOut and obj is self.edit:
            self._refresh_state(hovered=False, focused=False)
        return super().eventFilter(obj, event)
