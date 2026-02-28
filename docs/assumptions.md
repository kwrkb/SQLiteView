# Assumptions for SQLite View

- Primary target platforms are Ubuntu/Linux (primary development), Windows (confirmed working), and macOS (untested). Python >= 3.10 is required.
- End users install the application on desktop environments where X11/Wayland (Linux) or native window system (Windows/macOS) is available for GUI rendering.
- PyQt6 wheels are acceptable for bundling within the Debian package; no system Qt dependencies are required. On Windows, PyQt6 bundles all necessary dependencies.
- Users operate on local SQLite databases; remote connections are out of scope.
- Database files are expected to fit in memory for paging 1,000-row chunks; extremely large tables may require streaming in a future iteration.
- Debian packaging leverages native Python tooling and `dpkg-deb`; `fpm` or other third-party packagers are not required on target systems.
- CI runs on GitHub-hosted Ubuntu runners with internet access to install Python dependencies.
- UI is English-only. Japanese documentation (`README_ja.md`) is provided separately.
