from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from sqliteviewer.database import DatabaseError, DatabaseService


class DatabaseServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "sample.db"
        self._populate_database(self.db_path)
        self.service = DatabaseService()
        self.service.open(self.db_path)

    def tearDown(self) -> None:
        self.service.close()
        self.tmpdir.cleanup()

    def _populate_database(self, path: Path) -> None:
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        conn.executemany(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            [
                ("Alice", 30),
                ("Bob", 24),
                ("Carol", 27),
            ],
        )
        conn.execute("CREATE VIEW adult_users AS SELECT * FROM users WHERE age >= 25")
        conn.commit()
        conn.close()

    def test_list_tables_includes_tables_and_views(self) -> None:
        tables = self.service.list_tables()
        self.assertIn("users", tables)
        self.assertIn("adult_users", tables)

    def test_table_preview_truncates(self) -> None:
        result = self.service.get_table_preview("users", limit=2)
        self.assertEqual(len(result.rows), 2)
        self.assertTrue(result.truncated)
        self.assertEqual(result.row_count, 3)
        self.assertEqual(result.columns, ["id", "name", "age"])

    def test_execute_query_restricts_writes(self) -> None:
        with self.assertRaises(DatabaseError):
            self.service.execute_query("UPDATE users SET age = age + 1")

        result = self.service.execute_query("SELECT name FROM users ORDER BY id DESC")
        self.assertEqual([row[0] for row in result.rows], ["Carol", "Bob", "Alice"])

    def test_schema_contains_create_statement(self) -> None:
        schema = self.service.get_table_schema("users")
        self.assertIn("CREATE TABLE", schema)
        self.assertIn("users", schema)


if __name__ == "__main__":
    unittest.main()
