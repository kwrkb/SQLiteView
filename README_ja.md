# Ubuntu用SQLiteビューア
⚠️ このリポジトリは Codex などの AI ツールでの実験成果です。  
学習目的で公開しており、安定性やサポートは保証しません。

Ubuntuデスクトップをターゲットにした、軽量なPyQt6製デスクトップSQLiteデータベースビューアです。このアプリでは、テーブルの閲覧、アドホックなクエリの実行、結果のエクスポートが可能です。PythonホイールまたはDebianパッケージ形式で配布されます。

## 機能

- ページネーション付きでテーブルを閲覧し、行データを表示
- シンタックスハイライトとCSVエクスポート機能を備えたカスタムSQLクエリの実行
- テーブルスキーマのメタデータを表示
- 素早いアクセスのための最近使用したファイル一覧の永続化
- Ubuntu用のDebianパッケージビルダー（Python依存バンドル）

## 前提条件

このアプリケーションをUbuntuにインストールするには、以下のシステムライブラリが必要です:

```bash
sudo apt-get update
sudo apt-get install -y libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-xkb1
```

## はじめに

```bash
# 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate

# 開発用追加機能と共に編集可能モードでインストール
pip install --upgrade pip
pip install -e ".[dev]"
```

`zsh` などでは `".[dev]"` 部分をクォートしておくと、グロブ展開されずに extras 指定がそのまま渡せます。

`uv` を利用する場合は、事前に（例: `pip install uv`）インストールした上で、仮想環境内で `uv pip install -e ".[dev]"` を実行してください。

ビューアの起動:

```bash
sqliteviewer /path/to/database.sqlite
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
