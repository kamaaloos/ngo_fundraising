"""Screen-aware window sizing shared by login and main window.

Keeps windows inside the usable desktop (taskbar-safe) with compact defaults
that match local `python main.py` behavior in packaged installs too.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QApplication, QWidget

# Qt's historic QWIDGETSIZE_MAX ((1 << 24) - 1); not exported by all PySide6 builds.
_QWIDGETSIZE_MAX = 16777215


def available_desktop() -> QRect:
    app = QApplication.instance()
    screen = app.primaryScreen() if app is not None else None
    if screen is None:
        return QRect(0, 0, 1280, 800)
    # Prefer the screen under the cursor when multiple monitors exist.
    try:
        from PySide6.QtGui import QCursor

        at_cursor = app.screenAt(QCursor.pos()) if app is not None else None
        if at_cursor is not None:
            screen = at_cursor
    except Exception:
        pass
    return screen.availableGeometry()


def fit_window(
    window: QWidget,
    *,
    prefer_width: int,
    prefer_height: int,
    min_width: int = 720,
    min_height: int = 480,
    margin: int = 28,
    height_ratio: float = 0.90,
    width_ratio: float = 0.96,
    center: bool = True,
) -> None:
    """Resize ``window`` to a compact size that always fits the desktop.

    Does not clamp maximum size — that blocked the Windows maximize control.
    Skips resize/move when the window is already maximized or full-screen.
    """
    if window.isMaximized() or window.isFullScreen():
        return
    # If Qt reports a maximized window state before the native show completes.
    state = window.windowState()
    if state & (Qt.WindowState.WindowMaximized | Qt.WindowState.WindowFullScreen):
        return

    available = available_desktop()
    usable_w = max(640, available.width() - margin * 2)
    usable_h = max(480, available.height() - margin * 2)

    max_w = max(min_width, int(usable_w * width_ratio))
    max_h = max(min_height, int(usable_h * height_ratio))

    target_w = min(prefer_width, max_w)
    target_h = min(prefer_height, max_h)
    target_w = max(min(min_width, max_w), target_w)
    target_h = max(min(min_height, max_h), target_h)

    window.setMinimumSize(min(min_width, max_w), min(min_height, max_h))
    # Leave maximize / manual grow unrestricted (title-bar maximize control).
    window.setMaximumSize(_QWIDGETSIZE_MAX, _QWIDGETSIZE_MAX)
    window.resize(target_w, target_h)

    if center:
        frame = window.frameGeometry()
        frame.moveCenter(available.center())
        # Keep the frame inside available geometry.
        x = min(max(frame.x(), available.x()), available.right() - frame.width() + 1)
        y = min(max(frame.y(), available.y()), available.bottom() - frame.height() + 1)
        window.move(x, y)
