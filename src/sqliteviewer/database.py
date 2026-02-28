"""Database access layer for SQLite database interactions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import sqlite3


DEFAULT_ROW_LIMIT = 200
QUERY_ROW_LIMIT = 1000

_READ_KEYWORDS = {"SELECT", "WITH", "PRAGMA", "EXPLAIN"}
_DML_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "REPLACE"}
_DDL_KEYWORDS = {"CREATE", "ALTER", "DROP"}
_TCL_KEYWORDS = {"BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT", "RELEASE"}


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""


@dataclass(slots=True)
class QueryResult:
    """Container for tabular data returned to the UI layer."""

    columns: List[str]
    rows: List[Sequence[object]]
    truncated: bool = False
    row_count: Optional[int] = None
    affected_rows: Optional[int] = None
    is_write_operation: bool = False


class DatabaseService:
    """High-level helper for SQLite database interactions."""

    def __init__(self) -> None:
        self._connection: Optional[sqlite3.Connection] = None
        self._path: Optional[str] = None

    @property
    def path(self) -> Optional[str]:
        return self._path

    def open(self, database_path: str | Path) -> None:
        """Open a SQLite database, closing any previous connection."""

        path = Path(database_path).expanduser().resolve()
        if not path.exists():
            raise DatabaseError(f"Database file not found: {path}")

        self.close()

        try:
            conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to open database: {exc}") from exc

        self._connection = conn
        self._path = str(path)

    def close(self) -> None:
        """Close the active database connection if present."""

        if self._connection is not None:
            self._connection.close()
        self._connection = None
        self._path = None

    def list_tables(self) -> List[str]:
        """Return user tables ordered alphabetically."""

        rows = self._execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') "
            "AND name NOT LIKE 'sqlite_%' ORDER BY lower(name)"
        )
        return [row[0] for row in rows]

    def get_table_preview(self, table_name: str, limit: int = DEFAULT_ROW_LIMIT, offset: int = 0) -> QueryResult:
        """Return a preview of the given table."""

        connection = self._ensure_connection()
        quoted_table = self._quote_identifier(table_name)

        try:
            cursor = connection.execute(
                f"SELECT * FROM {quoted_table} LIMIT ? OFFSET ?",
                (limit + 1, offset),
            )
            rows = cursor.fetchmany(limit + 1)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to fetch table '{table_name}': {exc}") from exc

        columns = [description[0] for description in cursor.description or []]
        truncated = len(rows) > limit
        trimmed_rows = [tuple(row) for row in rows[:limit]]
        row_count = self._get_table_row_count(table_name)
        return QueryResult(columns=columns, rows=trimmed_rows, truncated=truncated, row_count=row_count)

    def get_table_schema(self, table_name: str) -> str:
        """Return the CREATE statement for the table if available."""

        rows = self._execute(
            "SELECT sql FROM sqlite_master WHERE name = ? AND type IN ('table', 'view')",
            (table_name,),
        )
        if not rows or rows[0][0] is None:
            return "Schema information not found."
        return rows[0][0]

    def execute_query(self, sql: str, limit: int = QUERY_ROW_LIMIT) -> QueryResult:
        """Execute a SQL statement and return results."""

        self._ensure_connection()
        sql = sql.strip()
        if not sql:
            raise DatabaseError("Query is empty.")

        try:
            cursor = self._connection.execute(sql)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to execute query: {exc}") from exc

        if cursor.description is None:
            # Write operation (INSERT/UPDATE/DELETE/DDL/TCL)
            affected = cursor.rowcount if cursor.rowcount >= 0 else None
            return QueryResult(
                columns=[],
                rows=[],
                affected_rows=affected,
                is_write_operation=True,
            )

        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchmany(limit + 1)
        truncated = len(rows) > limit
        trimmed_rows = [tuple(row) for row in rows[:limit]]
        return QueryResult(columns=columns, rows=trimmed_rows, truncated=truncated)

    def classify_query(self, sql: str) -> str:
        """Classify a SQL statement as read/dml/ddl/tcl/unknown."""

        keyword = self._extract_first_keyword(sql)
        if keyword is None:
            return "unknown"
        if keyword in _READ_KEYWORDS:
            return "read"
        if keyword in _DML_KEYWORDS:
            return "dml"
        if keyword in _DDL_KEYWORDS:
            return "ddl"
        if keyword in _TCL_KEYWORDS:
            return "tcl"
        return "unknown"

    def is_destructive_query(self, sql: str) -> Tuple[bool, str]:
        """Detect potentially destructive queries.

        Returns (is_destructive, reason). Checks for:
        - DROP statements
        - DELETE without a WHERE clause
        """

        keyword = self._extract_first_keyword(sql)
        if keyword == "DROP":
            return True, "This will permanently drop the object."
        if keyword == "DELETE":
            stripped = self._strip_sql_noise(sql).upper()
            if "WHERE" not in stripped:
                return True, "DELETE without WHERE will remove all rows."
        return False, ""

    def _strip_sql_noise(self, sql: str) -> str:
        """Remove SQL comments and string literals from a statement."""

        result = []
        i = 0
        length = len(sql)
        while i < length:
            if sql[i] == '-' and i + 1 < length and sql[i + 1] == '-':
                newline = sql.find('\n', i + 2)
                i = length if newline == -1 else newline + 1
            elif sql[i] == '/' and i + 1 < length and sql[i + 1] == '*':
                end = sql.find('*/', i + 2)
                i = length if end == -1 else end + 2
            elif sql[i] == "'":
                i += 1
                while i < length:
                    if sql[i] == "'" and (i + 1 >= length or sql[i + 1] != "'"):
                        i += 1
                        break
                    if sql[i] == "'" and i + 1 < length and sql[i + 1] == "'":
                        i += 2
                    else:
                        i += 1
            else:
                result.append(sql[i])
                i += 1
        return ''.join(result)

    def _get_table_row_count(self, table_name: str) -> Optional[int]:
        """Return row count for table; failure returns None."""

        try:
            rows = self._execute(
                f"SELECT COUNT(*) FROM {self._quote_identifier(table_name)}"
            )
        except DatabaseError:
            return None
        return int(rows[0][0]) if rows else None

    def _execute(self, sql: str, parameters: Iterable[object] | None = None):
        connection = self._ensure_connection()
        try:
            cursor = connection.execute(sql, tuple(parameters or []))
            return cursor.fetchall()
        except sqlite3.Error as exc:
            raise DatabaseError(str(exc)) from exc

    def _ensure_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise DatabaseError("No database open.")
        return self._connection

    def _quote_identifier(self, identifier: str) -> str:
        if not identifier:
            raise DatabaseError("Identifier cannot be empty.")
        return '"' + identifier.replace('"', '""') + '"'

    def _extract_first_keyword(self, sql: str) -> Optional[str]:
        index = 0
        length = len(sql)
        while index < length:
            char = sql[index]
            if char.isspace():
                index += 1
                continue
            if char == '-' and index + 1 < length and sql[index + 1] == '-':
                newline = sql.find('\n', index + 2)
                index = length if newline == -1 else newline + 1
                continue
            if char == '/' and index + 1 < length and sql[index + 1] == '*':
                end = sql.find('*/', index + 2)
                index = length if end == -1 else end + 2
                continue
            if char in '([':
                index += 1
                continue
            start = index
            while index < length and (sql[index].isalpha() or sql[index] == '_'):
                index += 1
            if start != index:
                return sql[start:index].upper()
            index += 1
        return None

    def __del__(self) -> None:  # pragma: no cover - best effort cleanup
        try:
            self.close()
        except Exception:
            pass
