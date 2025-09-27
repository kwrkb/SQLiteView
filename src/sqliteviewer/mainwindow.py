"""Main window implementation for the SQLite viewer."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableView,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
    QHBoxLayout,
)

from .database import DatabaseError, DatabaseService, QueryResult
from .resources import load_icon
from .sql_highlighter import SqlHighlighter


MAX_RECENT_FILES = 5


class MainWindow(QMainWindow):
    """Top-level application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SQLite Viewer")
        self.resize(1100, 700)
        self.setWindowIcon(load_icon())

        self.database_service = DatabaseService()
        self.settings = QSettings("SQLiteViewer", "App")
        self.query_result: Optional[QueryResult] = None

        self.table_list = QListWidget()
        self.table_list.itemSelectionChanged.connect(self._on_table_selected)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)

        self.schema_view = QTextEdit()
        self.schema_view.setReadOnly(True)
        self.schema_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.query_editor = QPlainTextEdit()
        self.query_editor.setPlaceholderText("Write a read-only SQL query…")
        self.query_editor.setTabStopDistance(4 * self.query_editor.fontMetrics().horizontalAdvance(' '))
        SqlHighlighter(self.query_editor.document())

        self.query_result_view = QTableView()
        self.query_result_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.query_result_view.setAlternatingRowColors(True)
        self.query_result_view.horizontalHeader().setStretchLastSection(True)

        self.query_status_label = QLabel("Ready")

        self._build_ui()
        self._build_menus()
        self._load_recent_files()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_container.setLayout(left_layout)
        left_layout.addWidget(QLabel("Tables"))
        left_layout.addWidget(self.table_list)
        splitter.addWidget(left_container)

        right_tabs = QTabWidget()
        splitter.addWidget(right_tabs)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        table_tab = QWidget()
        table_layout = QVBoxLayout()
        table_tab.setLayout(table_layout)
        table_layout.addWidget(self.table_view)
        right_tabs.addTab(table_tab, "Data Preview")

        schema_tab = QWidget()
        schema_layout = QVBoxLayout()
        schema_tab.setLayout(schema_layout)
        schema_layout.addWidget(self.schema_view)
        right_tabs.addTab(schema_tab, "Schema")

        query_tab = QWidget()
        query_layout = QVBoxLayout()
        query_tab.setLayout(query_layout)

        query_layout.addWidget(self.query_editor)

        button_bar = QHBoxLayout()
        run_button = QPushButton("Run Query")
        run_button.clicked.connect(self._run_query)
        export_button = QPushButton("Export Results")
        export_button.clicked.connect(self._export_results)
        button_bar.addWidget(run_button)
        button_bar.addWidget(export_button)
        button_bar.addStretch(1)
        query_layout.addLayout(button_bar)

        query_layout.addWidget(self.query_result_view)
        query_layout.addWidget(self.query_status_label)

        right_tabs.addTab(query_tab, "SQL Console")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.setCentralWidget(central)

    def _build_menus(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open…", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_dialog)
        file_menu.addAction(open_action)

        self.recent_menu = QMenu("Open Recent", self)
        file_menu.addMenu(self.recent_menu)

        close_action = QAction("Close Database", self)
        close_action.triggered.connect(self._close_database)
        file_menu.addAction(close_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _open_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open SQLite Database", str(Path.home()), "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)")
        if path:
            self.open_database(path)

    def open_database(self, path: str) -> None:
        try:
            self.database_service.open(path)
        except DatabaseError as exc:
            QMessageBox.critical(self, "Unable to open database", str(exc))
            return

        self.status_bar.showMessage(f"Opened {path}", 4000)
        self.setWindowTitle(f"SQLite Viewer — {Path(path).name}")
        self._refresh_tables()
        self._remember_recent_file(path)

    def _refresh_tables(self) -> None:
        self.table_list.clear()

        try:
            tables = self.database_service.list_tables()
        except DatabaseError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        if not tables:
            self.status_bar.showMessage("No tables found.")
            return

        for table in tables:
            QListWidgetItem(table, self.table_list)

        self.table_list.setCurrentRow(0)

    def _close_database(self) -> None:
        self.database_service.close()
        self.table_list.clear()
        self.table_view.setModel(None)
        self.schema_view.clear()
        self.query_result_view.setModel(None)
        self.status_bar.showMessage("Database closed.", 3000)
        self.setWindowTitle("SQLite Viewer")

    def _on_table_selected(self) -> None:
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            return
        table_name = selected_items[0].text()
        self._load_table_preview(table_name)
        self._load_table_schema(table_name)

    def _load_table_preview(self, table_name: str) -> None:
        try:
            result = self.database_service.get_table_preview(table_name)
        except DatabaseError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        self._populate_table(self.table_view, result)
        message = f"Loaded {table_name}"
        if result.row_count is not None:
            message += f" — {result.row_count} rows"
        if result.truncated:
            message += " (showing first chunk)"
        self.status_bar.showMessage(message, 5000)

    def _load_table_schema(self, table_name: str) -> None:
        try:
            schema = self.database_service.get_table_schema(table_name)
        except DatabaseError as exc:
            QMessageBox.warning(self, "Schema unavailable", str(exc))
            schema = "Schema information not found."
        self.schema_view.setPlainText(schema)

    def _populate_table(self, view: QTableView, result: QueryResult) -> None:
        from PyQt6.QtGui import QStandardItem, QStandardItemModel

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(result.columns)
        for row in result.rows:
            items = [QStandardItem(str(value) if value is not None else "NULL") for value in row]
            model.appendRow(items)
        view.setModel(model)

    def _run_query(self) -> None:
        query = self.query_editor.toPlainText()
        try:
            result = self.database_service.execute_query(query)
        except DatabaseError as exc:
            QMessageBox.critical(self, "Query failed", str(exc))
            return

        self.query_result = result
        self._populate_table(self.query_result_view, result)
        status = f"Returned {len(result.rows)} row(s)"
        if result.truncated:
            status += " (truncated)"
        self.query_status_label.setText(status)
        self.status_bar.showMessage("Query executed successfully.", 4000)

    def _export_results(self) -> None:
        if not self.query_result or not self.query_result.columns:
            QMessageBox.information(self, "Export", "No query results to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", str(Path.home() / "query_results.csv"), "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(self.query_result.columns)
                writer.writerows(self.query_result.rows)
        except OSError as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
            return

        self.status_bar.showMessage(f"Exported results to {path}", 5000)

    def _show_about_dialog(self) -> None:
        QMessageBox.about(
            self,
            "About SQLite Viewer",
            "<b>SQLite Viewer</b><br/>Version 0.1.0<br/><br/>"
            "A lightweight desktop viewer for SQLite databases.",
        )

    def _load_recent_files(self) -> None:
        files = self.settings.value("recent_files", [], type=list)
        self._recent_files = [f for f in files if Path(f).exists()]
        self._update_recent_menu()

    def _remember_recent_file(self, path: str) -> None:
        files = [Path(path).as_posix()]
        files.extend(f for f in getattr(self, "_recent_files", []) if f != path)
        self._recent_files = files[:MAX_RECENT_FILES]
        self.settings.setValue("recent_files", self._recent_files)
        self._update_recent_menu()

    def _update_recent_menu(self) -> None:
        self.recent_menu.clear()
        if not getattr(self, "_recent_files", []):
            action = QAction("(No recent files)", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
            return

        for path in self._recent_files:
            action = QAction(path, self)
            action.triggered.connect(lambda checked=False, p=path: self.open_database(p))
            self.recent_menu.addAction(action)

        self.recent_menu.addSeparator()
        clear_action = QAction("Clear Recent", self)
        clear_action.triggered.connect(self._clear_recent_files)
        self.recent_menu.addAction(clear_action)

    def _clear_recent_files(self) -> None:
        self._recent_files = []
        self.settings.remove("recent_files")
        self._update_recent_menu()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt API)
        self.database_service.close()
        event.accept()
