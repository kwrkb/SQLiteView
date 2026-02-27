"""Simple SQL syntax highlighter for the query editor."""

from __future__ import annotations

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter


class SqlHighlighter(QSyntaxHighlighter):
    """Applies formatting rules to highlight SQL keywords and tokens."""

    KEYWORDS = {
        # Read / query
        "SELECT",
        "FROM",
        "WHERE",
        "GROUP",
        "BY",
        "ORDER",
        "LIMIT",
        "OFFSET",
        "JOIN",
        "LEFT",
        "RIGHT",
        "INNER",
        "OUTER",
        "ON",
        "AS",
        "AND",
        "OR",
        "NOT",
        "NULL",
        "IS",
        "IN",
        "CASE",
        "WHEN",
        "THEN",
        "END",
        "DISTINCT",
        "WITH",
        "UNION",
        "ALL",
        "HAVING",
        "LIKE",
        "EXISTS",
        "PRAGMA",
        "BETWEEN",
        "EXCEPT",
        "INTERSECT",
        "ELSE",
        "EXPLAIN",
        # DML
        "INSERT",
        "UPDATE",
        "DELETE",
        "SET",
        "VALUES",
        "INTO",
        "REPLACE",
        # DDL
        "CREATE",
        "ALTER",
        "DROP",
        "TABLE",
        "VIEW",
        "INDEX",
        "TRIGGER",
        "COLUMN",
        "ADD",
        "RENAME",
        "IF",
        "PRIMARY",
        "KEY",
        "UNIQUE",
        "CHECK",
        "DEFAULT",
        "FOREIGN",
        "REFERENCES",
        "CONSTRAINT",
        "AUTOINCREMENT",
        # TCL
        "BEGIN",
        "COMMIT",
        "ROLLBACK",
        "TRANSACTION",
        "SAVEPOINT",
        "RELEASE",
        # Maintenance
        "VACUUM",
        "REINDEX",
        "ATTACH",
        "DETACH",
        "CASCADE",
        "RESTRICT",
        "CONFLICT",
        "ABORT",
        "FAIL",
        "IGNORE",
        "TEMPORARY",
        "TEMP",
        # Type names
        "INTEGER",
        "TEXT",
        "REAL",
        "BLOB",
        "NUMERIC",
    }

    def __init__(self, document) -> None:
        super().__init__(document)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#005cc5"))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6a737d"))
        self.comment_format.setFontItalic(True)

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#22863a"))

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#b31d28"))

        self.comment_expression = QRegularExpression(r"--[^\n]*")
        self.string_expression = QRegularExpression(r"'([^']|'')*'")
        self.number_expression = QRegularExpression(r"\b\d+(\.\d+)?\b")

        self.keyword_patterns = []
        for keyword in self.KEYWORDS:
            pattern = QRegularExpression(rf"\b{keyword}\b")
            pattern.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
            self.keyword_patterns.append(pattern)

    def highlightBlock(self, text: str) -> None:  # noqa: N802 (Qt API signature)
        for pattern in self.keyword_patterns:
            self._apply_regex(pattern, text, self.keyword_format)
        self._apply_regex(self.comment_expression, text, self.comment_format)
        self._apply_regex(self.string_expression, text, self.string_format)
        self._apply_regex(self.number_expression, text, self.number_format)

    def _apply_regex(self, expression: QRegularExpression, text: str, fmt: QTextCharFormat) -> None:
        iterator = expression.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(start, length, fmt)
