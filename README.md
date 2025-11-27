# SQLite Viewer for Ubuntu
⚠️ This repository is an experimental project using AI tools such as Codex.  
It is shared for educational purposes only. Please note that it is provided *as is*, without warranty or official support.

A lightweight PyQt6 desktop SQLite database viewer targeting Ubuntu desktops. The app lets you inspect tables, run ad-hoc queries, and export results—packaged for distribution via Python wheels or Debian packages.

## Features

- Browse tables and view row data with pagination
- Run custom SQL queries with syntax highlighting and CSV export
- Display table schema metadata
- Persistent recent files list for quick access
- Debian package builder for Ubuntu (Python-dependent bundle)

## Prerequisites

This application requires the following system libraries to be installed on Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-xkb1
```

## Getting Started

### Option 1: Using uv (Recommended)

This project is set up to work with [uv](https://github.com/astral-sh/uv), a fast Python package manager.

#### Development Setup

```bash
# Install dependencies (creates .venv automatically)
uv sync --dev

# Run the application locally
uv run sqliteview /path/to/database.sqlite

# Or run without arguments to browse for a database
uv run sqliteview
```

#### Global Installation

Install the tool globally to use it from anywhere:

```bash
# Install from GitHub (easiest - no need to clone)
uv tool install git+https://github.com/kwrkb/SQLiteView.git

# Or install from local directory
uv tool install .

# Now you can run it from anywhere
sqliteview /path/to/database.sqlite
```

### Option 2: Traditional pip Method

```bash
# Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev extras
pip install --upgrade pip
pip install -e ".[dev]"

# Launch the viewer
sqliteview /path/to/database.sqlite
```

## Running Tests

```bash
pytest
```

## Packaging

- Build wheel + sdist: `python -m build`
- Build Debian package: `./scripts/build_deb.sh`
- Generated packages are placed in `dist/`

## Continuous Integration

GitHub Actions workflow (`.github/workflows/ci.yml`) validates formatting, runs tests, and ensures packaging succeeds on Ubuntu.

## License

Released under the MIT License. See [LICENSE](LICENSE).
