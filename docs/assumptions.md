# Assumptions for Ubuntu SQLite Viewer

- Target platform is Ubuntu 22.04 LTS or newer with Python >= 3.10 preinstalled.
- End users install the application on desktop environments where X11/Wayland is available for GUI rendering.
- PyQt6 wheels are acceptable for bundling within the Debian package; no system Qt dependencies are required.
- Users operate on local SQLite databases; remote connections are out of scope.
- Database files are expected to fit in memory for paging 1,000-row chunks; extremely large tables may require streaming in a future iteration.
- Packaging leverages native Python tooling and `dpkg-deb`; `fpm` or other third-party packagers are not required on target systems.
- CI runs on GitHub-hosted Ubuntu runners with internet access to install Python dependencies.
- Application internationalization/localization is not required for this release; English-only UI is acceptable.
