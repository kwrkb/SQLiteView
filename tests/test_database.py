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

    def test_execute_query_allows_writes(self) -> None:
        result = self.service.execute_query("UPDATE users SET age = age + 1 WHERE name = 'Alice'")
        self.assertTrue(result.is_write_operation)
        self.assertEqual(result.affected_rows, 1)

        select = self.service.execute_query("SELECT age FROM users WHERE name = 'Alice'")
        self.assertEqual(select.rows[0][0], 31)

    def test_execute_query_insert(self) -> None:
        result = self.service.execute_query("INSERT INTO users (name, age) VALUES ('Dave', 20)")
        self.assertTrue(result.is_write_operation)
        self.assertEqual(result.affected_rows, 1)

        count = self.service.execute_query("SELECT COUNT(*) FROM users")
        self.assertEqual(count.rows[0][0], 4)

    def test_execute_query_delete(self) -> None:
        result = self.service.execute_query("DELETE FROM users WHERE name = 'Bob'")
        self.assertTrue(result.is_write_operation)
        self.assertEqual(result.affected_rows, 1)

        count = self.service.execute_query("SELECT COUNT(*) FROM users")
        self.assertEqual(count.rows[0][0], 2)

    def test_execute_query_ddl_create_drop(self) -> None:
        create = self.service.execute_query(
            "CREATE TABLE products (id INTEGER PRIMARY KEY, label TEXT)"
        )
        self.assertTrue(create.is_write_operation)
        self.assertIn("products", self.service.list_tables())

        drop = self.service.execute_query("DROP TABLE products")
        self.assertTrue(drop.is_write_operation)
        self.assertNotIn("products", self.service.list_tables())

    def test_execute_query_transaction_rollback(self) -> None:
        self.service.execute_query("BEGIN")
        self.service.execute_query("INSERT INTO users (name, age) VALUES ('Eve', 22)")
        self.service.execute_query("ROLLBACK")

        count = self.service.execute_query("SELECT COUNT(*) FROM users")
        self.assertEqual(count.rows[0][0], 3)

    def test_classify_query(self) -> None:
        self.assertEqual(self.service._classify_query("SELECT 1"), "read")
        self.assertEqual(self.service._classify_query("WITH cte AS (SELECT 1) SELECT * FROM cte"), "read")
        self.assertEqual(self.service._classify_query("PRAGMA table_info(users)"), "read")
        self.assertEqual(self.service._classify_query("EXPLAIN SELECT 1"), "read")
        self.assertEqual(self.service._classify_query("INSERT INTO users VALUES (1,'a',1)"), "dml")
        self.assertEqual(self.service._classify_query("UPDATE users SET age=1"), "dml")
        self.assertEqual(self.service._classify_query("DELETE FROM users"), "dml")
        self.assertEqual(self.service._classify_query("REPLACE INTO users VALUES (1,'a',1)"), "dml")
        self.assertEqual(self.service._classify_query("CREATE TABLE t (id INTEGER)"), "ddl")
        self.assertEqual(self.service._classify_query("ALTER TABLE users ADD COLUMN email TEXT"), "ddl")
        self.assertEqual(self.service._classify_query("DROP TABLE users"), "ddl")
        self.assertEqual(self.service._classify_query("BEGIN"), "tcl")
        self.assertEqual(self.service._classify_query("COMMIT"), "tcl")
        self.assertEqual(self.service._classify_query("ROLLBACK"), "tcl")
        self.assertEqual(self.service._classify_query("-- comment\nSELECT 1"), "read")

    def test_is_destructive_query(self) -> None:
        is_d, reason = self.service.is_destructive_query("DROP TABLE users")
        self.assertTrue(is_d)
        self.assertIn("drop", reason.lower())

        is_d, reason = self.service.is_destructive_query("DELETE FROM users")
        self.assertTrue(is_d)
        self.assertIn("WHERE", reason)

        is_d, _ = self.service.is_destructive_query("DELETE FROM users WHERE id = 1")
        self.assertFalse(is_d)

        is_d, _ = self.service.is_destructive_query("SELECT * FROM users")
        self.assertFalse(is_d)

    def test_schema_contains_create_statement(self) -> None:
        schema = self.service.get_table_schema("users")
        self.assertIn("CREATE TABLE", schema)
        self.assertIn("users", schema)


if __name__ == "__main__":
    unittest.main()
