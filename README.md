# Blenderアドオン最小構成（交差モデル作成）

このリポジトリには、**2つ以上の面（メッシュ）またはカーブを選択して、1ボタンで交差部分をモデル化**する Blender アドオンの最小構成を用意しています。

## 構成

- `blender_min_addon/__init__.py`
  - `bl_info`
  - `Operator` (`minimal.build_intersection`)
  - `Panel` (3D View の Sidebar に表示)
  - `register()` / `unregister()`

## できること

- 複数オブジェクト（`MESH`, `CURVE`, `SURFACE`, `FONT`）を選択
- ボタン1つで共通の交差領域を新規メッシュ `Intersection_Result` として生成

## インストール手順

1. `blender_min_addon` ディレクトリをZIP化（ZIPの直下に `__init__.py` が来る形）。
2. Blenderを開く。
3. `Edit > Preferences > Add-ons > Install...` を選択。
4. 作成したZIPを選択してインストール。
5. Add-on一覧で **Cross_obj** を有効化。

## 使い方

1. 交差させたいオブジェクトを2つ以上選択。
2. 3D View の右サイドバー（`N`キー）→ **Cross_obj** タブを開く。
3. **交差モデルを作成** を押す。
4. `Intersection_Result` が生成され、交差領域のみが残ります。

## 注意

- 交差が存在しない場合、空メッシュになることがあります（警告表示）。
- 処理結果は新規オブジェクトとして作成され、元オブジェクトはそのまま残ります。
