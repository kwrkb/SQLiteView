# Architecture Overview

## High-level components

1. **Application entrypoint (`sqliteviewer.__main__`)**
   - Parses CLI arguments and bootstraps the Qt event loop.
   - Delegates to the GUI application module.
2. **GUI layer (`sqliteviewer.app`)**
   - Implements the main window, table browser, query editor, and result views using PyQt6 widgets.
   - Separates UI widgets from data access via signal/slot connections.
3. **Data access layer (`sqliteviewer.database`)**
   - Provides `DatabaseService` for opening SQLite files, listing tables, describing schemas, executing queries (read and write), and streaming rows.
   - Supports DML (INSERT/UPDATE/DELETE), DDL (CREATE/DROP/ALTER), and TCL (BEGIN/COMMIT/ROLLBACK).
   - Includes query classification (`classify_query`) and destructive operation detection (`is_destructive_query`) with SQL noise stripping for safe keyword matching.
   - Includes pragmatic safeguards (e.g., limiting returned rows) to keep the UI responsive.
4. **Theme system (`sqliteviewer.theme`)**
   - Manages light/dark theme switching via QSS stylesheets.
   - Persists user preference via `QSettings`.
5. **SQL syntax highlighter (`sqliteviewer.sql_highlighter`)**
   - Provides real-time syntax highlighting for the query editor.
   - Supports theme-aware color schemes (light/dark).
6. **Utility module (`sqliteviewer.resources`)**
   - Manages application metadata, version, and icon loading.
   - Includes QSS theme files (`light.qss`, `dark.qss`) and desktop integration assets.

## Data flow

```
User action -> Qt signal -> MainWindow slot -> DatabaseService call -> sqlite3 -> results
```

Results are translated into Qt models (`QStandardItemModel`) before reaching the view layer, ensuring the UI remains decoupled from the database cursor lifecycle.

## Packaging & distribution

- Python packaging via `pyproject.toml` (hatchling backend).
- CLI/desktop entry point exposed as `sqliteview` console script.
- Debian packaging script (`scripts/build_deb.sh`) leverages `python -m build` and `dpkg-deb` to produce `.deb` including bundled dependencies.
- Desktop integration provides `.desktop` launcher and application icon installed by the Debian package.

## Tooling & automation

- `Makefile` orchestrates common tasks (`install`, `test`, `lint`, `build`, `package`).
- Unit tests (`pytest`) validate the data access layer and SQL utilities.
- GitHub Actions workflow (`.github/workflows/ci.yml`) runs linting, tests, and build validation on Ubuntu runners.
