"""Access-control helpers for repository operations."""

from __future__ import annotations

from app.auth.session import current_session


class AccessDenied(PermissionError):
    """Raised when the current session cannot perform an action."""


def require_auth() -> None:
    if not current_session.is_authenticated:
        raise AccessDenied("Sign in required.")


def require_admin() -> None:
    require_auth()
    if not current_session.is_admin:
        raise AccessDenied("Administrator access required.")


def require_project_access(project_id: int | None) -> None:
    require_auth()
    if project_id is None:
        raise AccessDenied("Project required.")
    if not current_session.can_access_project(int(project_id)):
        raise AccessDenied("You are not assigned to this project.")


def accessible_project_ids() -> list[int] | None:
    """None means all projects (admin). Otherwise the assigned id list."""
    require_auth()
    if current_session.is_admin:
        return None
    return list(current_session.project_ids)
