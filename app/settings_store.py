"""User appearance settings (theme, day/night, organization logo)."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from app.db.database import APP_DIR

SETTINGS_PATH = APP_DIR / "ui_settings.json"
USER_LOGO_PATH = APP_DIR / "user_logo.png"

THEME_PRESETS = {
    "teal": {
        "label": "Teal (default)",
        "accent": "#176B5B",
        "accent_hover": "#125747",
        "accent_pressed": "#0E493D",
        "accent_soft": "#E3F3EF",
        "accent_soft_border": "#5EBFB0",
    },
    "blue": {
        "label": "Ocean blue",
        "accent": "#1D4ED8",
        "accent_hover": "#1E40AF",
        "accent_pressed": "#1E3A8A",
        "accent_soft": "#DBEAFE",
        "accent_soft_border": "#60A5FA",
    },
    "violet": {
        "label": "Violet",
        "accent": "#7C3AED",
        "accent_hover": "#6D28D9",
        "accent_pressed": "#5B21B6",
        "accent_soft": "#EDE9FE",
        "accent_soft_border": "#A78BFA",
    },
    "amber": {
        "label": "Amber",
        "accent": "#D97706",
        "accent_hover": "#B45309",
        "accent_pressed": "#92400E",
        "accent_soft": "#FEF3C7",
        "accent_soft_border": "#FBBF24",
    },
    "rose": {
        "label": "Rose",
        "accent": "#E11D48",
        "accent_hover": "#BE123C",
        "accent_pressed": "#9F1239",
        "accent_soft": "#FFE4E6",
        "accent_soft_border": "#FB7185",
    },
    "forest": {
        "label": "Forest",
        "accent": "#15803D",
        "accent_hover": "#166534",
        "accent_pressed": "#14532D",
        "accent_soft": "#DCFCE7",
        "accent_soft_border": "#4ADE80",
    },
}

MODES = {
    "day": "Day (light)",
    "night": "Night (dark)",
}

DEFAULT_BACKUP_REMINDER_DAYS = 7


@dataclass
class UISettings:
    theme: str = "teal"
    mode: str = "day"
    has_user_logo: bool = False
    backup_on_exit: bool = True
    backup_reminder_days: int = DEFAULT_BACKUP_REMINDER_DAYS

    def accent_key(self) -> str:
        return self.theme if self.theme in THEME_PRESETS else "teal"

    def mode_key(self) -> str:
        return self.mode if self.mode in MODES else "day"


def load_settings() -> UISettings:
    if not SETTINGS_PATH.exists():
        return UISettings(has_user_logo=USER_LOGO_PATH.exists())
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return UISettings(has_user_logo=USER_LOGO_PATH.exists())
    reminder = data.get("backup_reminder_days", DEFAULT_BACKUP_REMINDER_DAYS)
    try:
        reminder_days = max(1, int(reminder))
    except (TypeError, ValueError):
        reminder_days = DEFAULT_BACKUP_REMINDER_DAYS
    return UISettings(
        theme=str(data.get("theme") or "teal"),
        mode=str(data.get("mode") or "day"),
        has_user_logo=USER_LOGO_PATH.exists(),
        backup_on_exit=bool(data.get("backup_on_exit", True)),
        backup_reminder_days=reminder_days,
    )


def save_settings(settings: UISettings) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "theme": settings.accent_key(),
        "mode": settings.mode_key(),
        "backup_on_exit": bool(settings.backup_on_exit),
        "backup_reminder_days": int(settings.backup_reminder_days),
    }
    SETTINGS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def set_user_logo(source_path: str | Path) -> Path:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Logo file not found: {source}")
    USER_LOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Normalize to PNG via copy; Qt can load common formats from path too,
    # but we keep a stable filename for the sidebar.
    suffix = source.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}:
        if suffix != ".png":
            try:
                from PIL import Image

                Image.open(source).convert("RGBA").save(USER_LOGO_PATH, "PNG")
            except Exception:
                shutil.copy2(source, USER_LOGO_PATH.with_suffix(suffix))
                return USER_LOGO_PATH.with_suffix(suffix)
        else:
            shutil.copy2(source, USER_LOGO_PATH)
    else:
        raise ValueError("Use a PNG, JPG, WEBP, BMP, or GIF image.")
    settings = load_settings()
    settings.has_user_logo = True
    save_settings(settings)
    return USER_LOGO_PATH


def clear_user_logo() -> None:
    if USER_LOGO_PATH.exists():
        USER_LOGO_PATH.unlink()
    for alt in USER_LOGO_PATH.parent.glob("user_logo.*"):
        try:
            alt.unlink()
        except OSError:
            pass
    settings = load_settings()
    settings.has_user_logo = False
    save_settings(settings)


def user_logo_path() -> Path | None:
    if USER_LOGO_PATH.exists():
        return USER_LOGO_PATH
    for alt in sorted(APP_DIR.glob("user_logo.*")):
        return alt
    return None
