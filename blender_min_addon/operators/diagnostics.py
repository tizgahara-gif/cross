import json
import time

import bpy


def _find_root_from_active(context):
    active = context.active_object
    if not active or "prig_rig_id" not in active:
        return None
    rig_id = active["prig_rig_id"]
    roots = [obj for obj in bpy.data.objects if obj.type == 'EMPTY' and obj.get("prig_rig_id") == rig_id and obj.get("prig_grid_obj")]
    return roots[0] if roots else None


class PRIG_OT_diagnostics(bpy.types.Operator):
    bl_idname = "prig.diagnostics"
    bl_label = "Diagnostics"

    def execute(self, context):
        root = _find_root_from_active(context)
        if not root:
            self.report({'ERROR'}, "Rig Root が見つかりません。")
            return {'CANCELLED'}

        errors = []
        warnings = []

        surface_name = root.get("prig_surface_obj", "")
        surface_obj = bpy.data.objects.get(surface_name)
        if not surface_obj:
            errors.append("参照サーフェスが欠損")
        elif surface_obj.type != 'MESH':
            errors.append("参照サーフェスがMeshではない")

        curve_names = json.loads(root.get("prig_curve_objs", "[]"))
        for cname in curve_names:
            cobj = bpy.data.objects.get(cname)
            if not cobj:
                errors.append(f"Curve欠損: {cname}")
            elif cobj.type != 'CURVE':
                errors.append(f"Curve型不正: {cname}")

        target_names = json.loads(root.get("prig_target_objs", "[]"))
        for tname in target_names:
            tobj = bpy.data.objects.get(tname)
            if not tobj:
                errors.append(f"Target欠損: {tname}")
            elif tobj.type != 'MESH':
                errors.append(f"Target型不正: {tname}")

        grid_name = root.get("prig_grid_obj", "")
        grid_obj = bpy.data.objects.get(grid_name)
        if not grid_obj:
            errors.append("Projection Grid欠損")

        # Lightweight cycle hint: if surface has same rig tag and has deform mod targeting target objects.
        if surface_obj and surface_obj.get("prig_rig_id") == root.get("prig_rig_id"):
            for mod in surface_obj.modifiers:
                if getattr(mod, "object", None) and mod.object.name in target_names:
                    warnings.append("依存循環の兆候: Surface modifier may depend on Target")

        root["prig_last_diagnostics_ms"] = int(time.time() * 1000)

        if errors:
            self.report({'ERROR'}, " / ".join(errors[:3]))
            return {'CANCELLED'}

        if warnings:
            self.report({'WARNING'}, " / ".join(warnings[:3]))
        else:
            self.report({'INFO'}, "Diagnostics passed")
        return {'FINISHED'}


CLASSES = (PRIG_OT_diagnostics,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
