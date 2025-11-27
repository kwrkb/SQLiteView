# SQLite View
⚠️ このリポジトリは Codex などの AI ツールでの実験成果です。
学習目的で公開しており、安定性やサポートは保証しません。

軽量なクロスプラットフォーム対応のPyQt6製デスクトップSQLiteデータベースビューアです。このアプリでは、テーブルの閲覧、アドホックなクエリの実行、結果のエクスポートが可能です。PythonホイールまたはDebianパッケージ形式で配布されます。

## 機能

- ページネーション付きでテーブルを閲覧し、行データを表示
- シンタックスハイライトとCSVエクスポート機能を備えたカスタムSQLクエリの実行
- テーブルスキーマのメタデータを表示
- 素早いアクセスのための最近使用したファイル一覧の永続化
- Ubuntu用のDebianパッケージビルダー（Python依存バンドル）

## 動作確認済みプラットフォーム

- ✅ **Windows** - 動作確認済み
- ✅ **Ubuntu/Linux** - 主要開発環境
- ⏳ **macOS** - 未検証（フィードバック歓迎！）

## 前提条件

### Ubuntu/Linux

以下のシステムライブラリが必要です:

```bash
sudo apt-get update
sudo apt-get install -y libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-xkb1
```

### Windows

追加のシステムライブラリは不要です。PyQt6が必要な依存関係をすべて含んでいます。

### macOS

追加のシステムライブラリは不要です（未検証）。

## はじめに

### 方法1: uv を使う（推奨）

このプロジェクトは高速なPythonパッケージマネージャー [uv](https://github.com/astral-sh/uv) で動作するように設定されています。

#### 開発環境のセットアップ

```bash
# 依存関係をインストール（自動的に .venv が作成されます）
uv sync --dev

# アプリケーションをローカルで実行
uv run sqliteview /path/to/database.sqlite

# または引数なしで実行してデータベースを選択
uv run sqliteview
```

#### グローバルインストール

ツールをグローバルにインストールして、どこからでも使用できるようにします:

```bash
# GitHubから直接インストール（最も手軽 - クローン不要）
uv tool install git+https://github.com/kwrkb/SQLiteView.git

# またはローカルディレクトリからインストール
uv tool install .

# これでどこからでも実行可能
sqliteview /path/to/database.sqlite
```

### 方法2: 従来の pip を使う方法

```bash
# 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate

# 開発用追加機能と共に編集可能モードでインストール
pip install --upgrade pip
pip install -e ".[dev]"

# ビューアの起動
sqliteview /path/to/database.sqlite
```

## テストの実行

```bash
pytest
```

## パッケージング

- wheel + sdist のビルド: `python -m build`
- Debian パッケージのビルド: `./scripts/build_deb.sh`
- 生成されたパッケージは `dist/` に配置されます

## 継続的インテグレーション

GitHub Actions ワークフロー (`.github/workflows/ci.yml`) は、フォーマットの検証、テストの実行、Ubuntuでのパッケージングの成功を保証します。

## ライセンス

MITライセンスの下でリリースされています。[LICENSE](LICENSE) を参照してください。
