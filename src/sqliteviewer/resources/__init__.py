"""Resource helpers for the SQLite viewer."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Optional

from PyQt6.QtGui import QIcon


def resource_path(name: str) -> str:
    """Return the filesystem path to a resource bundled with the package."""

    with resources.as_file(resources.files(__package__).joinpath(name)) as path:
        return str(path)


def load_icon() -> QIcon:
    """Load the application icon."""

    icon_path = resource_path("icon.png")
    return QIcon(icon_path)
