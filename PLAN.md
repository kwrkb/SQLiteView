# SQLiteView 開発計画

## Context

SQLiteViewは現在、読み取り専用のSQLiteビューア（SELECT/WITH/PRAGMAのみ許可）。
これをINSERT/UPDATE/DELETE/CREATE/DROP等の書き込みクエリも実行可能なSQLクライアントに拡張する。

## 変更対象ファイル

- `src/sqliteviewer/database.py` — DB層: 読み取り制限の解除、クエリ分類、結果型の拡張
- `src/sqliteviewer/mainwindow.py` — UI層: 書き込み結果の表示、確認ダイアログ、自動リフレッシュ
- `src/sqliteviewer/sql_highlighter.py` — ハイライト: 書き込み系キーワード追加
- `tests/test_database.py` — テスト: 書き込み系テストの追加

## 実装ステップ

### Step 1: database.py — DB層の変更（完了）

- [x] `QueryResult` に `affected_rows: Optional[int]` と `is_write_operation: bool` を追加
- [x] `classify_query()` を追加 — `read`/`dml`/`ddl`/`tcl`/`unknown` を返す（公開メソッド）
- [x] `is_destructive_query()` を追加 — DROP・WHERE無しDELETEを検出し `(bool, reason)` を返す
- [x] `_strip_sql_noise()` を追加 — コメント(`--`, `/* */`)・文字列リテラル(`'...'`)・ダブルクォート識別子(`"..."`)を除去（WHERE句バイパス防止）
- [x] `execute_query()` を書き換え — `_assert_read_only()` 削除、`cursor.description is None` で書き込み判定
- [x] `_assert_read_only()` を削除
- [x] docstring `"read-only SQLite interactions"` → `"SQLite database interactions"` に更新

> 接続設定（`isolation_level=None`）は変更なし。ユーザーが明示的に BEGIN/COMMIT/ROLLBACK でトランザクション制御可能。

### Step 2: tests/test_database.py — テスト更新（完了）

- [x] `test_execute_query_restricts_writes` → `test_execute_query_allows_writes` に置換（UPDATE実行→affected_rows確認→SELECT で結果検証）
- [x] INSERT のテストを追加
- [x] DELETE のテストを追加
- [x] DDL（CREATE TABLE / DROP TABLE）のテストを追加
- [x] トランザクション（BEGIN→INSERT→ROLLBACK）のテストを追加
- [x] クエリ分類（`classify_query`）のテストを追加
- [x] 破壊的操作検出（`is_destructive_query`）のテストを追加

> 16テストすべて pass 確認済み（初期10 + Multi AI Audit対応で6追加）。

### Step 3: sql_highlighter.py — キーワード追加（完了）

- [x] DML キーワードを追加: INSERT, UPDATE, DELETE, SET, VALUES, INTO, REPLACE
- [x] DDL キーワードを追加: CREATE, ALTER, DROP, TABLE, VIEW, INDEX, TRIGGER, COLUMN, ADD, RENAME, IF, PRIMARY, KEY, UNIQUE, CHECK, DEFAULT, FOREIGN, REFERENCES, CONSTRAINT, AUTOINCREMENT
- [x] TCL キーワードを追加: BEGIN, COMMIT, ROLLBACK, TRANSACTION, SAVEPOINT, RELEASE
- [x] その他を追加: BETWEEN, EXCEPT, INTERSECT, ELSE, EXPLAIN, VACUUM, REINDEX, ATTACH, DETACH, CASCADE, RESTRICT, CONFLICT, ABORT, FAIL, IGNORE, TEMPORARY, TEMP
- [x] 型名を追加: INTEGER, TEXT, REAL, BLOB, NUMERIC

### Step 4: mainwindow.py — UI層の変更（完了）

- [x] プレースホルダー更新: `"Write a read-only SQL query…"` → `"Write a SQL statement…"`
- [x] `_run_query()` を書き換え — 破壊的クエリの確認ダイアログ（`QMessageBox.warning`）追加
- [x] 書き込み結果の表示: `"{N} row(s) affected"` または `"Statement executed successfully"`
- [x] `_refresh_after_write()` を追加 — DDL後はテーブルリスト・プレビュー・スキーマをリフレッシュ、DML後は選択中テーブルのプレビューをリフレッシュ
- [x] write操作後に `self.query_result = None` をリセット — 古いSELECT結果が誤ってExportされる問題を修正
- [x] `_refresh_tables()` を改善 — リフレッシュ後に以前の選択テーブルを復元
- [x] About ダイアログのバージョンを `0.1.0` → `0.2.1` に修正

## 検証方法

```bash
# ユニットテスト実行
uv run python -m pytest tests/ -v

# 手動テスト（GUIが使える場合）
uv run sqliteview test.db
# → INSERT/UPDATE/DELETE/CREATE TABLE/DROP TABLE/BEGIN/ROLLBACK を実行し動作確認
```

## 現状

**実装完了・マージ済み。** 全ステップの実装・テストが完了しており、16テストすべて pass。
SQLiteView は INSERT/UPDATE/DELETE/CREATE/DROP/BEGIN/COMMIT/ROLLBACK 等の書き込みクエリを実行可能な SQL クライアントとなった。

### マージ履歴

**PR #3: 書き込みサポート** — マージ完了（2026-02-27）
- レビュー指摘対応・CIエラー修正を含む

**PR #4: Multi AI Audit コンセンサス所見の修正** — マージ完了（2026-02-28）
- 12件のコンセンサス所見を修正（セキュリティ・コード品質・ビルド・テスト）
- PRレビュー対応:
  - `build_deb.sh`: `tomllib`（Python 3.11+）→ `grep`/`sed` に置換（Python 3.10互換性復元）
  - `_strip_sql_noise()`: ダブルクォート識別子の除去を追加（セキュリティ強化）
  - エラーパステスト6件追加（空クエリ、無効SQL、未接続操作、存在しないファイル、文字列リテラル内WHERE）

**PR #5: UI/UX改善（ダークモード・モノスペースフォント・ショートカット）** — マージ完了（2026-02-28）
- フェーズ2全タスク実装
- PRレビュー対応:
  - `_SETTINGS_GROUP` → `SETTINGS_GROUP` に公開化し、`theme.py` と `mainwindow.py` で定数共有
  - ショートカットコンテキスト変更提案はスキップ（SQL IDE標準のWindowShortcut維持）

---

## フェーズ2: UI/UX 改善（完了）

### Context

機能は十分だが、UIスタイリングが一切なくシステムネイティブテーマのまま。ダークモード非対応、SQLエディタのフォント未指定、ショートカットも最低限(Ctrl+O/Q のみ)。開発者ツールとしての使い勝手を底上げする。

### 変更対象ファイル

**新規作成:**
- `src/sqliteviewer/theme.py` — Theme enum, QSS読み込み/適用/永続化 (~60行)
- `src/sqliteviewer/resources/light.qss` — ライトテーマ QSS (~180行)
- `src/sqliteviewer/resources/dark.qss` — ダークテーマ QSS (~180行)

**変更:**
- `src/sqliteviewer/app.py` — 起動時テーマ適用 (+3行)
- `src/sqliteviewer/mainwindow.py` — View メニュー、テーマ切替、フォント、ショートカット (+~40行)
- `src/sqliteviewer/sql_highlighter.py` — テーマ連動カラースキーム追加 (+~25行)

### Step 5: テーマ基盤 + ダークモード（完了）

- [x] `theme.py` を作成 — `Theme` enum (LIGHT/DARK)、`load_theme()`/`apply_theme()`/`save_theme_preference()`/`load_theme_preference()`
  > `StrEnum`(3.11+) → `str, Enum`(3.10+) に修正済み（`requires-python >= 3.10` 互換）
- [x] `light.qss` を作成 — GitHub風パレット (bg `#ffffff`, fg `#24292e`, accent `#0366d6`)
  - 対象: QMainWindow, QTableView, QTabWidget, QListWidget, QPlainTextEdit, QTextEdit, QPushButton, QSplitter, QMenuBar, QMenu, QStatusBar, QScrollBar, QHeaderView
  - ボタン hover/pressed 効果、タブ選択インジケーター、スリムスクロールバー、角丸4px
- [x] `dark.qss` を作成 — VS Code dark 風パレット (bg `#1e1e1e`, fg `#d4d4d4`, accent `#4fc1ff`)
- [x] `app.py` を変更 — `window.show()` 前に `apply_theme(load_theme_preference())` を呼ぶ
- [x] `mainwindow.py` に View メニュー追加 — "Toggle Dark Mode" (Ctrl+D)
- [x] `sql_highlighter.py` に `set_color_scheme()` 追加 — ライト (GitHub風) / ダーク (VS Code風) の2パレットを切替、`rehighlight()` で即反映
- [x] `mainwindow.py` でハイライター参照を保持し、テーマ切替時に色同期
  > テーマ設定は `QSettings(*SETTINGS_GROUP)` の `theme` キーへ保存し、起動時に `app.py` で先に適用する。`SETTINGS_GROUP` は `theme.py` で定義し `mainwindow.py` からインポート。

### Step 6: モノスペースフォント（完了）

- [x] `QFontDatabase.systemFont(SystemFont.FixedFont)` でモノスペースフォント取得、11pt
- [x] `query_editor` と `schema_view` に適用
- [x] フォント設定後に `setTabStopDistance` を再計算

### Step 7: キーボードショートカット（完了）

- [x] `Ctrl+Enter` / `F5` — クエリ実行 (`QShortcut` で query_editor にバインド)
- [x] `Ctrl+R` — テーブルリフレッシュ (View メニューにアクション追加)
- [x] Run Query ボタンにツールチップ `"Execute SQL (Ctrl+Enter)"` 追加

### 設計判断

- **QSS方式** — QPaletteより柔軟 (hover/角丸/スクロールバー)、外部ライブラリ不要
- **テーマ2種のみ** — Light/Dark。レジストリパターンは over-engineering
- **QFontDatabase.systemFont** — フォント名ハードコードより確実なクロスプラットフォーム対応
- **QShortcut** — eventFilter やサブクラス化より軽量

### 検証方法

```bash
# 回帰テスト
uv run python -m pytest tests/ -v

# 手動テスト
uv run python -m sqliteviewer
# → View > Toggle Dark Mode で切替確認
# → SQLエディタがモノスペースフォントか確認
# → Ctrl+Enter / F5 でクエリ実行確認
# → Ctrl+R でテーブルリフレッシュ確認
# → アプリ再起動後にテーマ維持されるか確認
```

## 現状

フェーズ2まで実装・マージ済み（PR #5）。SQLiteView はライト/ダークテーマ切替、固定幅フォントの SQL エディタ/スキーマ表示、`Ctrl+Enter`・`F5`・`Ctrl+R` の操作に対応した。レビューで `StrEnum`(3.11+) の Python 3.10 非互換を検出し `str, Enum` に修正、`QSettings` グループの定数共有化も対応済み。
