"""Theme helpers for the SQLite viewer."""

from __future__ import annotations

from enum import Enum

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication

from .resources import resource_path


class Theme(str, Enum):
    """Supported application themes."""

    LIGHT = "light"
    DARK = "dark"


SETTINGS_GROUP = ("SQLiteViewer", "App")
_THEME_KEY = "theme"


def load_theme(theme: Theme) -> str:
    """Load the QSS content for the requested theme."""

    stylesheet_path = resource_path(f"{theme.value}.qss")
    with open(stylesheet_path, encoding="utf-8") as stylesheet_file:
        return stylesheet_file.read()


def apply_theme(theme: Theme, app: QApplication | None = None) -> Theme:
    """Apply the requested theme to the current application."""

    current_app = app or QApplication.instance()
    if current_app is None:
        raise RuntimeError("QApplication must exist before applying a theme.")

    current_app.setStyleSheet(load_theme(theme))
    current_app.setProperty("theme", theme.value)
    return theme


def save_theme_preference(theme: Theme) -> None:
    """Persist the theme preference."""

    settings = QSettings(*SETTINGS_GROUP)
    settings.setValue(_THEME_KEY, theme.value)


def load_theme_preference() -> Theme:
    """Load the persisted theme preference."""

    settings = QSettings(*SETTINGS_GROUP)
    stored_theme = settings.value(_THEME_KEY, Theme.LIGHT.value, type=str)
    try:
        return Theme(stored_theme)
    except ValueError:
        return Theme.LIGHT
