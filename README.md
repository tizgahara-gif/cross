# Projection Rig（Blender Add-on v1）

Curve + Reference Surface から Projection Grid を生成し、Target を追従変形させるための Blender 4.x 向けアドオンです。

## 実装構成

- `blender_min_addon/__init__.py` : エントリーポイント（登録）
- `blender_min_addon/props.py` : `PRIG_Settings`（UI/設定プロパティ）
- `blender_min_addon/operators/create_rig.py` : Create / Update / Select / Duplicate
- `blender_min_addon/operators/bake.py` : Bake Grid / Bake Target
- `blender_min_addon/operators/diagnostics.py` : 入力・整合性チェック
- `blender_min_addon/ui/panel.py` : Nパネル `Projection Rig` UI
- `blender_min_addon/nodes/node_groups.py` : GNグループ生成

## 主要機能（v1）

- 3D View > Sidebar に `Projection Rig` タブを追加。
- `Create Rig` で以下を自動生成。
  - `PRIG_{id}_ROOT`（Rig Root Empty）
  - `PRIG_{id}_GRID`（Projection Grid）
  - `PRIG_{id}_NG_GRID`（GNグループ）
  - `PRIG_{id}_COLL`（管理コレクション）
- Gridへ Shrinkwrap（投影）を設定。
- Targetへ Surface Deform を追加し、Bind 実行を試行。
- Rig Root に `prig_*` カスタムプロパティを保存。
- `Bake Grid` / `Bake Target` で現在形状を複製ベイク。
- `Diagnostics` で入力型・欠損・軽量な循環兆候を検査。

## 使い方（最小ケース）

1. `Reference Surface` に Mesh を指定。
2. `Curve A~C` に 1本以上の Curve を指定。
3. `Target A~C` に 1つ以上の Mesh を指定。
4. `Create Rig` 実行。
5. 必要に応じて `Update Rig` / `Bake` / `Diagnostics` を使用。

## 注意

- v1 はプロダクション向け骨格実装です。GN内部の高度な投影計算（距離/接線フィールド駆動）は今後拡張前提です。
- Blenderの `bpy.ops.object.surfacedeform_bind` はコンテキスト条件に依存するため、シーン状態によってBind成否が変わる場合があります。
