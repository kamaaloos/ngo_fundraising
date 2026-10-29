"""App logo and window icon helpers."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLabel

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
ICON_PATH = ASSETS_DIR / "app.ico"

# Unique ID so Windows taskbar does not reuse the python.exe icon.
WINDOWS_APP_ID = "MayleSoft.NGOFundraising.Desktop"

COPYRIGHT_TEXT = (
    "© 2026 MayleSoft NGO-fund app · Developed by Hasan Kamaal"
)


def configure_windows_app_id() -> None:
    """Must run before QApplication() so the taskbar uses our window icon."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(  # type: ignore[attr-defined]
            WINDOWS_APP_ID
        )
    except (AttributeError, OSError):
        pass


def _hex_to_colorref(hex_color: str) -> int:
    """Windows COLORREF is 0x00BBGGRR."""
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return 0
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return r | (g << 8) | (b << 16)


def apply_windows_titlebar_theme(window, *, dark: bool, caption_hex: str | None = None) -> None:
    """Theme the native Windows title bar (Qt stylesheets cannot style it).

    Uses DWM immersive dark mode + (on Win11) caption/text colors.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        return

    try:
        hwnd = int(window.winId())
    except Exception:
        return
    if not hwnd:
        return

    dwmapi = ctypes.windll.dwmapi
    # 20 = supported on Win10 2004+; 19 was used on some insider builds.
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36
    DWMWA_BORDER_COLOR = 34

    dark_flag = wintypes.BOOL(1 if dark else 0)
    for attr in (DWMWA_USE_IMMERSIVE_DARK_MODE, 19):
        try:
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                attr,
                ctypes.byref(dark_flag),
                ctypes.sizeof(dark_flag),
            )
            break
        except Exception:
            continue

    if caption_hex:
        try:
            caption = wintypes.DWORD(_hex_to_colorref(caption_hex))
            text = wintypes.DWORD(_hex_to_colorref("#FFFFFF" if dark else "#111827"))
            border = caption
            dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(caption), ctypes.sizeof(caption)
            )
            dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_TEXT_COLOR, ctypes.byref(text), ctypes.sizeof(text)
            )
            dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_BORDER_COLOR, ctypes.byref(border), ctypes.sizeof(border)
            )
        except Exception:
            # Older Windows builds ignore caption color attributes.
            pass


def logo_pixmap(max_width: int = 180, max_height: int = 180) -> QPixmap:
    pix = QPixmap(str(LOGO_PATH)) if LOGO_PATH.exists() else QPixmap()
    if pix.isNull():
        return pix
    return pix.scaled(
        max_width,
        max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def app_icon() -> QIcon:
    # Prefer cropped .ico so the glyph fills the Windows taskbar / title bar.
    if ICON_PATH.exists():
        icon = QIcon(str(ICON_PATH))
        if not icon.isNull():
            return icon

    # Fallback: crop transparent padding from the logo, then scale.
    icon = QIcon()
    source = ASSETS_DIR / "app_icon.png"
    path = source if source.exists() else LOGO_PATH
    if not path.exists():
        return icon
    full = QPixmap(str(path))
    if full.isNull():
        return icon
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(
            full.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
    return icon


def logo_label(
    max_width: int = 160,
    max_height: int = 120,
    *,
    object_name: str = "appLogo",
) -> QLabel:
    label = QLabel()
    label.setObjectName(object_name)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    apply_app_logo(label, max_width, max_height)
    return label


def apply_app_logo(label: QLabel, max_width: int, max_height: int) -> None:
    """Scale the MayleSoft / app mark into an existing QLabel."""
    pix = logo_pixmap(max_width, max_height)
    if pix.isNull():
        label.setText("NGO Fundraising")
        return
    label.setPixmap(pix)
    label.setToolTip("NGO Fundraising")
    label.setMinimumSize(0, 0)
    label.setMaximumSize(max_width + 8, max_height + 8)


def user_logo_pixmap(max_width: int = 160, max_height: int = 72) -> QPixmap:
    """Organization logo chosen in Settings (not the app logo)."""
    from app.settings_store import user_logo_path

    path = user_logo_path()
    if path is None:
        return QPixmap()
    pix = QPixmap(str(path))
    if pix.isNull():
        return pix
    return pix.scaled(
        max_width,
        max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def apply_user_logo(label: QLabel, max_width: int = 160, max_height: int = 72) -> None:
    pix = user_logo_pixmap(max_width, max_height)
    if pix.isNull():
        label.clear()
        label.hide()
        return
    label.setPixmap(pix)
    label.setToolTip("Organization logo")
    label.show()


def copyright_label(*, object_name: str = "copyrightLabel") -> QLabel:
    label = QLabel(COPYRIGHT_TEXT)
    label.setObjectName(object_name)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    return label
