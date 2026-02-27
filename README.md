# Blenderアドオン最小構成（交差モデル作成）

このリポジトリには、**X軸 / Y軸 / Z軸の3スロットから元オブジェクトを選択し、1ボタンで交差部分をモデル化**する Blender アドオンの最小構成を用意しています。

## 構成

- `blender_min_addon/__init__.py`
  - `bl_info`
  - `Operator` (`cross_obj.build_intersection`)
  - `Panel` (3D View の Sidebar > Tool に表示)
  - `Scene` プロパティ（X/Y/Z の元オブジェクト指定）
  - `register()` / `unregister()`

## できること

- `MESH`, `CURVE`, `SURFACE`, `FONT` を X/Y/Z の各スロットへ指定
- X/Y/Z のうち **2つ以上** 指定すると、共通交差領域を `Intersection_Result` として生成

## インストール手順

1. `blender_min_addon` ディレクトリをZIP化（ZIPの直下に `__init__.py` が来る形）。
2. Blenderを開く。
3. `Edit > Preferences > Add-ons > Install...` を選択。
4. 作成したZIPを選択してインストール。
5. Add-on一覧で **Cross_obj** を有効化。

## 使い方

1. 3D View の右サイドバー（`N`キー）→ **Tool** タブを開く。
2. `Cross_obj` パネルで X / Y / Z の元オブジェクトを指定。
3. **交差モデルを作成** を押す。
4. `Intersection_Result` が生成され、交差領域のみが残ります。

## 注意

- 同じオブジェクトを複数スロットに指定した場合は重複を除外して処理します。
- 交差が存在しない場合、空メッシュになることがあります（警告表示）。
- 処理結果は新規オブジェクトとして作成され、元オブジェクトはそのまま残ります。
