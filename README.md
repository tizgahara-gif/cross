# Projection Rig（Blender Add-on / 1ファイル構成）

このリポジトリのアドオンは、`blender_min_addon/__init__.py` に統合した**単一ファイル構成**です。

## 構成

- `blender_min_addon/__init__.py`
  - `bl_info`
  - PropertyGroup（`PRIG_Settings`）
  - Operators（Create / Update / Select / Duplicate / Bake / Diagnostics）
  - UI Panel（`Projection Rig` タブ）
  - GNノードグループ生成ヘルパー
  - depsgraph ハンドラ
  - `register()` / `unregister()`

## インストール

1. `blender_min_addon` ディレクトリをZIP化（ZIP直下に `__init__.py` がある形）。
2. Blenderで `Edit > Preferences > Add-ons > Install...` を選択。
3. ZIPを指定してインストール。
4. Add-on一覧で **Projection Rig** を有効化。

## 備考

- 以前の `props.py` / `operators/*` / `ui/*` / `nodes/*` は、1ファイル統合のため廃止しました。
