"""Application bootstrap helpers."""

from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from .mainwindow import MainWindow
from .theme import apply_theme, load_theme_preference


def run(initial_path: Optional[str] = None) -> int:
    """Launch the Qt application."""

    app = QApplication.instance()
    owns_app = False
    if app is None:
        app = QApplication(sys.argv)
        app.setApplicationName("SQLite View")
        app.setOrganizationName("SQLiteView")
        owns_app = True

    apply_theme(load_theme_preference(), app)
    window = MainWindow()
    window.show()

    if initial_path:
        QTimer.singleShot(0, lambda: window.open_database(initial_path))

    if owns_app:
        return app.exec()
    return 0
