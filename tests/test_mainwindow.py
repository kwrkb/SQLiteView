from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from PyQt6.QtCore import QSettings

from sqliteviewer.mainwindow import MainWindow


@pytest.fixture
def test_settings(qtbot) -> QSettings:
    """Override QSettings to use a temporary, clean .ini file for tests."""
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    settings = QSettings("test-org", "test-app")
    settings.clear()
    yield settings
    settings.clear()


def test_recent_files_are_purged_on_load(qtbot, test_settings, monkeypatch):
    """Verify that non-existent recent files are removed from settings on load."""
    # Arrange: Use monkeypatch to ensure the MainWindow uses our test_settings instance.
    monkeypatch.setattr(
        "sqliteviewer.mainwindow.QSettings", lambda *args, **kwargs: test_settings
    )

    with tempfile.NamedTemporaryFile() as tmpfile:
        real_path = Path(tmpfile.name).as_posix()
        fake_path = "/tmp/this-file-definitely-does-not-exist.db"
        initial_files = [real_path, fake_path]
        test_settings.setValue("recent_files", initial_files)

        # Act: create the main window, which should trigger the load
        window = MainWindow()
        qtbot.addWidget(window)

        # Assert: the settings should now only contain the real path
        stored_files = test_settings.value("recent_files", [], type=list)
        assert stored_files == [real_path]