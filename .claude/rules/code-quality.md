# Code Quality Rules

## 未使用 import を残さない
- import 文を追加・変更する際は、ファイル内で実際に使用されているか確認する
- `from X import a, b` で `b` を使わないなら `from X import a` にする
- 既存コードを変更して不要になった import も同時に削除する

## セキュリティチェックは初回から網羅的に実装する
- SQL のサニタイズ・検証ロジックを書く際は、コメント(`--`, `/* */`)と文字列リテラル(`'...'`)とダブルクォート識別子(`"..."`)をすべて考慮する
- 「まずコメントだけ対応して後でリテラルも」ではなく、初回実装ですべてのクォート形式をカバーする
- 文字列マッチングでキーワード検出する場合、ノイズ除去 → キーワード検出の順序を徹底する

## スクリプトのランチャーは `python3 -m` を使う
- Python パッケージの起動は `python3 path/to/__main__.py` ではなく `python3 -m module_name` を使う
- `__main__.py` を直接実行すると相対インポートが壊れる
- `PYTHONPATH` を適切に設定した上で `-m` で起動する
- 開発時は `uv run python -m sqliteviewer` を使う

## バージョン・定数の二重管理を避ける
- バージョン番号は `pyproject.toml` を Single Source of Truth とする
- シェルスクリプト等で必要な場合は `pyproject.toml` から動的に取得する（`grep`/`sed` を使い、Python の `tomllib` 等に依存しない）
- `requires-python` の最低バージョンで動作するか常に確認する（例: `tomllib` は 3.11+、`pyproject.toml` は `>=3.10`）
- ハードコードした定数が `pyproject.toml` と乖離していないか確認する

## 変更の波及先を確認する
- パッケージ名・バージョン等のプロジェクト全体に影響する変更時は、以下をすべて確認する:
  - `pyproject.toml`
  - `scripts/build_deb.sh`（ランチャー、DEBIAN/control、wheel ファイル名）
  - `scripts/run_app.sh`
- 一箇所だけ変更して他を放置しない

## Python 環境は uv を使う
- パッケージ管理・仮想環境・コマンド実行はすべて `uv` を使う
- テスト実行: `uv run python -m pytest tests/ -v`
- アプリ起動: `uv run python -m sqliteviewer`
- 依存追加: `uv add <package>`
- `pip install` や素の `python` コマンドは使わない
