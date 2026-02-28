"""Resource helpers for the SQLite viewer."""

from __future__ import annotations

from importlib import resources

from PyQt6.QtGui import QIcon


def resource_path(name: str) -> str:
    """Return the filesystem path to a resource bundled with the package."""

    return str(resources.files(__package__).joinpath(name))


def load_icon() -> QIcon:
    """Load the application icon."""

    icon_path = resource_path("icon.png")
    return QIcon(icon_path)
