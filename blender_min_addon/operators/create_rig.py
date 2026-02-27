import json
import time
import uuid

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty

from ..nodes.node_groups import ensure_grid_node_group


def _short_id(rig_id: str) -> str:
    return rig_id.split("-")[0].upper()


def _collect_curves(settings):
    return [
        obj
        for obj in (settings.control_curve_a, settings.control_curve_b, settings.control_curve_c)
        if obj
    ]


def _collect_targets(settings):
    return [obj for obj in (settings.target_a, settings.target_b, settings.target_c) if obj]


def _validate_inputs(settings):
    if not settings.reference_surface or settings.reference_surface.type != 'MESH':
        return False, "Reference Surface は Mesh を指定してください。"

    curves = _collect_curves(settings)
    if not curves or any(c.type != 'CURVE' for c in curves):
        return False, "Control Curves は1つ以上の Curve を指定してください。"

    targets = _collect_targets(settings)
    if not targets or any(t.type != 'MESH' for t in targets):
        return False, "Target は1つ以上の Mesh を指定してください。"

    return True, ""


def _create_grid_object(surface_obj, rig_id, u_res, v_res):
    sid = _short_id(rig_id)
    mesh = bpy.data.meshes.new(f"PRIG_{sid}_GRID_MESH")
    grid = bpy.data.objects.new(f"PRIG_{sid}_GRID", mesh)

    import bmesh

    bm = bmesh.new()
    bmesh.ops.create_grid(
        bm,
        x_segments=max(1, u_res - 1),
        y_segments=max(1, v_res - 1),
        size=0.5,
    )

    # simple regular UV for downstream bake/texturing usage.
    uv_layer = bm.loops.layers.uv.new("UVMap")
    min_u = float('inf')
    max_u = float('-inf')
    min_v = float('inf')
    max_v = float('-inf')
    for vert in bm.verts:
        min_u = min(min_u, vert.co.x)
        max_u = max(max_u, vert.co.x)
        min_v = min(min_v, vert.co.y)
        max_v = max(max_v, vert.co.y)
    du = max(max_u - min_u, 1e-8)
    dv = max(max_v - min_v, 1e-8)
    for face in bm.faces:
        for loop in face.loops:
            uv = loop[uv_layer].uv
            uv.x = (loop.vert.co.x - min_u) / du
            uv.y = (loop.vert.co.y - min_v) / dv

    bm.to_mesh(mesh)
    bm.free()

    dims = surface_obj.dimensions
    grid.scale = (max(0.001, dims.x), max(0.001, dims.y), 1.0)
    grid.matrix_world = surface_obj.matrix_world.copy()
    return grid


def _attach_projection_stack(grid_obj, surface_obj, rig_id):
    sid = _short_id(rig_id)

    ng = ensure_grid_node_group(f"PRIG_{sid}_NG_GRID")
    geo_mod = grid_obj.modifiers.new(name="PRIG_GN", type='NODES')
    geo_mod.node_group = ng

    shrink = grid_obj.modifiers.new(name="PRIG_Shrinkwrap", type='SHRINKWRAP')
    shrink.target = surface_obj
    shrink.wrap_method = 'PROJECT'
    shrink.wrap_mode = 'ON_SURFACE'
    shrink.use_project_z = True
    shrink.use_negative_direction = True
    shrink.use_positive_direction = True


def _bind_surface_deform(context, target, grid_obj):
    mod = target.modifiers.new(name="PRIG_SurfaceDeform", type='SURFACE_DEFORM')
    mod.target = grid_obj

    view_layer = context.view_layer
    prev_active = view_layer.objects.active
    prev_selected = [obj for obj in context.selected_objects]

    try:
        for obj in prev_selected:
            obj.select_set(False)
        target.select_set(True)
        view_layer.objects.active = target

        result = bpy.ops.object.surfacedeform_bind(modifier=mod.name)
        ok = result == {'FINISHED'}
        return ok, "" if ok else "Surface Deform bind failed"
    except Exception as exc:
        return False, str(exc)
    finally:
        target.select_set(False)
        for obj in prev_selected:
            if obj.name in bpy.data.objects:
                obj.select_set(True)
        if prev_active and prev_active.name in bpy.data.objects:
            view_layer.objects.active = prev_active


class PRIG_OT_create_rig(bpy.types.Operator):
    bl_idname = "prig.create_rig"
    bl_label = "Create Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.prig_settings
        valid, message = _validate_inputs(settings)
        if not valid:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        rig_id = str(uuid.uuid4())
        sid = _short_id(rig_id)
        surface = settings.reference_surface
        curves = _collect_curves(settings)
        targets = _collect_targets(settings)

        collection = bpy.data.collections.new(f"PRIG_{sid}_COLL")
        context.scene.collection.children.link(collection)

        root = bpy.data.objects.new(f"PRIG_{sid}_ROOT", None)
        root.empty_display_type = 'CUBE'
        collection.objects.link(root)

        grid = _create_grid_object(
            surface,
            rig_id,
            settings.grid_resolution_u,
            settings.grid_resolution_v,
        )
        collection.objects.link(grid)
        grid.parent = root

        _attach_projection_stack(grid, surface, rig_id)

        bind_failures = []
        for target in targets:
            ok, reason = _bind_surface_deform(context, target, grid)
            if not ok:
                bind_failures.append(f"{target.name}: {reason}")

        settings_blob = {
            "grid_resolution_u": settings.grid_resolution_u,
            "grid_resolution_v": settings.grid_resolution_v,
            "projection_method": settings.projection_method,
            "custom_vector": list(settings.custom_vector),
            "influence_radius": settings.influence_radius,
            "falloff_type": settings.falloff_type,
            "pin_borders": settings.pin_borders,
            "live_update": settings.live_update,
            "update_throttle_ms": settings.update_throttle_ms,
            "displacement_strength": settings.displacement_strength,
            "clamp": settings.clamp,
        }

        for obj in [root, grid, surface, *curves, *targets]:
            obj["prig_rig_id"] = rig_id

        root["prig_version"] = 1
        root["prig_rig_id"] = rig_id
        root["prig_surface_obj"] = surface.name
        root["prig_curve_objs"] = json.dumps([c.name for c in curves])
        root["prig_grid_obj"] = grid.name
        root["prig_target_objs"] = json.dumps([t.name for t in targets])
        root["prig_settings"] = json.dumps(settings_blob)
        root["prig_last_update_ms"] = int(time.time() * 1000)

        if bind_failures:
            self.report({'WARNING'}, "Bind失敗: " + " | ".join(bind_failures))
        else:
            self.report({'INFO'}, f"Projection Rig作成完了: {root.name}")
        return {'FINISHED'}


class PRIG_OT_update_rig(bpy.types.Operator):
    bl_idname = "prig.update_rig"
    bl_label = "Update Rig"

    def execute(self, context):
        active = context.active_object
        if not active or "prig_rig_id" not in active:
            self.report({'ERROR'}, "prig_rig_id を持つオブジェクトをアクティブにしてください。")
            return {'CANCELLED'}

        rig_id = active["prig_rig_id"]
        roots = [
            obj
            for obj in bpy.data.objects
            if obj.type == 'EMPTY' and obj.get("prig_rig_id") == rig_id and obj.get("prig_grid_obj")
        ]
        if not roots:
            self.report({'ERROR'}, "Rig Rootが見つかりません。")
            return {'CANCELLED'}

        root = roots[0]
        root["prig_last_update_ms"] = int(time.time() * 1000)
        self.report({'INFO'}, f"Rig updated: {root.name}")
        return {'FINISHED'}


class PRIG_OT_select_rig_objects(bpy.types.Operator):
    bl_idname = "prig.select_rig_objects"
    bl_label = "Select Rig Objects"

    def execute(self, context):
        active = context.active_object
        if not active or "prig_rig_id" not in active:
            self.report({'ERROR'}, "Rig オブジェクトを選択してください。")
            return {'CANCELLED'}

        rig_id = active["prig_rig_id"]
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in bpy.data.objects:
            if obj.get("prig_rig_id") == rig_id:
                obj.select_set(True)
        self.report({'INFO'}, "Rig objects selected")
        return {'FINISHED'}


class PRIG_OT_duplicate_rig(bpy.types.Operator):
    bl_idname = "prig.duplicate_rig"
    bl_label = "Duplicate Rig"

    share_references: BoolProperty(name="Share Surface/Curve/Target", default=True)

    def execute(self, context):
        active = context.active_object
        if not active or "prig_rig_id" not in active:
            self.report({'ERROR'}, "Rig オブジェクトを選択してください。")
            return {'CANCELLED'}

        old_id = active["prig_rig_id"]
        roots = [
            obj
            for obj in bpy.data.objects
            if obj.type == 'EMPTY' and obj.get("prig_rig_id") == old_id and obj.get("prig_grid_obj")
        ]
        if not roots:
            self.report({'ERROR'}, "Rig Root が見つかりません。")
            return {'CANCELLED'}

        root = roots[0]
        settings = context.scene.prig_settings
        settings.reference_surface = bpy.data.objects.get(root.get("prig_surface_obj"))

        curves = json.loads(root.get("prig_curve_objs", "[]"))
        targets = json.loads(root.get("prig_target_objs", "[]"))

        slots_c = ["control_curve_a", "control_curve_b", "control_curve_c"]
        slots_t = ["target_a", "target_b", "target_c"]

        for i, slot in enumerate(slots_c):
            setattr(settings, slot, bpy.data.objects.get(curves[i]) if i < len(curves) else None)
        for i, slot in enumerate(slots_t):
            setattr(settings, slot, bpy.data.objects.get(targets[i]) if i < len(targets) else None)

        bpy.ops.prig.create_rig()
        return {'FINISHED'}


@persistent
def _depsgraph_update_handler(scene, depsgraph):
    _ = depsgraph
    now_ms = int(time.time() * 1000)
    settings = scene.prig_settings if hasattr(scene, "prig_settings") else None
    if not settings or not settings.live_update:
        return

    throttle = max(1, settings.update_throttle_ms)
    for obj in scene.objects:
        if obj.type != 'EMPTY' or "prig_rig_id" not in obj or "prig_grid_obj" not in obj:
            continue
        last_ms = int(obj.get("prig_last_update_ms", 0))
        if now_ms - last_ms >= throttle:
            obj["prig_last_update_ms"] = now_ms


CLASSES = (
    PRIG_OT_create_rig,
    PRIG_OT_update_rig,
    PRIG_OT_select_rig_objects,
    PRIG_OT_duplicate_rig,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    if _depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_depsgraph_update_handler)


def unregister():
    if _depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_depsgraph_update_handler)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
