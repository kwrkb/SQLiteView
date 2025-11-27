"""CLI entry-point for SQLite Viewer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .app import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SQLite View application")
    parser.add_argument("database", nargs="?", help="Path to a SQLite database to open")
    parser.add_argument(
        "--version",
        action="version",
        version=f"SQLite View {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    initial_path = None
    if args.database:
        initial_path = str(Path(args.database).expanduser())

    return run(initial_path)


if __name__ == "__main__":
    sys.exit(main())
