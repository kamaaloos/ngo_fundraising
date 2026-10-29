"""Full-size branded splash shown while the app finishes starting."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from app.branding import COPYRIGHT_TEXT, LOGO_PATH
from app.i18n import tr


def _build_splash_pixmap(width: int = 720, height: int = 420) -> QPixmap:
    pix = QPixmap(width, height)
    pix.fill(QColor("#0B1C2E"))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Soft accent wash
    painter.fillRect(0, height - 90, width, 90, QColor("#12304A"))
    painter.fillRect(0, 0, 8, height, QColor("#176B5B"))

    logo = QPixmap(str(LOGO_PATH)) if LOGO_PATH.exists() else QPixmap()
    if not logo.isNull():
        scaled = logo.scaled(
            220,
            220,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        lx = (width - scaled.width()) // 2
        ly = 48
        painter.drawPixmap(lx, ly, scaled)
        text_top = ly + scaled.height() + 18
    else:
        text_top = 120

    title_font = QFont("Segoe UI", 26, QFont.Weight.Bold)
    painter.setFont(title_font)
    painter.setPen(QColor("#FFFFFF"))
    painter.drawText(
        40,
        text_top,
        width - 80,
        44,
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        tr("app.name"),
    )

    sub_font = QFont("Segoe UI", 12)
    painter.setFont(sub_font)
    painter.setPen(QColor("#8FA3BE"))
    painter.drawText(
        40,
        text_top + 48,
        width - 80,
        28,
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        "MayleSoft",
    )

    foot_font = QFont("Segoe UI", 10)
    painter.setFont(foot_font)
    painter.setPen(QColor("#6B8199"))
    painter.drawText(
        24,
        height - 52,
        width - 48,
        36,
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        COPYRIGHT_TEXT,
    )
    painter.end()
    return pix


def show_splash(app: QApplication | None = None) -> QSplashScreen:
    """Show a centered, professional splash; caller must finish() it later."""
    qapp = app or QApplication.instance()
    splash = QSplashScreen(
        _build_splash_pixmap(),
        Qt.WindowType.WindowStaysOnTopHint,
    )
    splash.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
    if qapp is not None:
        splash.setFont(qapp.font())
    splash.show()
    splash.raise_()
    if qapp is not None:
        qapp.processEvents()
    return splash
