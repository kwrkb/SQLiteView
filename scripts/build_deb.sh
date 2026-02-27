#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
BUILD_DIR="$DIST_DIR/deb_build"
PACKAGE="sqliteview"
VERSION="0.2.1"
ARCH="all"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/lib/$PACKAGE"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"

if ! python3 -c 'import build' >/dev/null 2>&1; then
  echo "Python package 'build' is required. Install it with 'pip install build'." >&2
  exit 1
fi

python3 -m build --wheel --outdir "$DIST_DIR"

WHEEL_FILE=$(ls "$DIST_DIR"/${PACKAGE}-${VERSION}-*.whl | head -n 1)
if [[ -z "$WHEEL_FILE" ]]; then
  echo "Wheel file not found. Aborting." >&2
  exit 1
fi

python3 - "$WHEEL_FILE" "$BUILD_DIR/usr/lib/$PACKAGE" <<'PY'
import sys
import zipfile
import pathlib
wheel = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])
with zipfile.ZipFile(wheel, 'r') as archive:
    archive.extractall(destination)
PY

cat <<EOF_CONTROL > "$BUILD_DIR/DEBIAN/control"
Package: $PACKAGE
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: SQLite Viewer Team <dev@example.com>
Depends: python3 (>= 3.10)
Description: PyQt6-based SQLite database client for Ubuntu.
 SQLiteView provides a desktop UI for browsing tables, running
 ad-hoc queries, and exporting results. Packaged with its Python
 dependencies.
EOF_CONTROL

cat <<EOF_EXEC > "$BUILD_DIR/usr/bin/$PACKAGE"
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="/usr/lib/$PACKAGE"
exec python3 "\$SCRIPT_DIR/sqliteviewer/__main__.py" "\$@"
EOF_EXEC
chmod +x "$BUILD_DIR/usr/bin/$PACKAGE"

install -m 644 "$ROOT_DIR/src/sqliteviewer/resources/sqliteviewer.desktop" "$BUILD_DIR/usr/share/applications/sqliteviewer.desktop"
install -m 644 "$ROOT_DIR/src/sqliteviewer/resources/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/sqliteviewer.png"

OUTPUT_DEB="$DIST_DIR/${PACKAGE}_${VERSION}_${ARCH}.deb"
rm -f "$OUTPUT_DEB"
dpkg-deb --build "$BUILD_DIR" "$OUTPUT_DEB"

rm -rf "$BUILD_DIR"
echo "Built Debian package: $OUTPUT_DEB"
