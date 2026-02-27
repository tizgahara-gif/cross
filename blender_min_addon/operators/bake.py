import json

import bpy


def _active_rig_root(context):
    active = context.active_object
    if not active or "prig_rig_id" not in active:
        return None

    rig_id = active["prig_rig_id"]
    roots = [
        obj
        for obj in bpy.data.objects
        if obj.type == 'EMPTY' and obj.get("prig_rig_id") == rig_id and obj.get("prig_grid_obj")
    ]
    return roots[0] if roots else None


def _link_object_to_context_collection(context, obj):
    collection = context.collection or context.scene.collection
    collection.objects.link(obj)


def _bake_object(context, obj, suffix):
    depsgraph = context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    baked_mesh = bpy.data.meshes.new_from_object(eval_obj, depsgraph=depsgraph)
    baked_obj = bpy.data.objects.new(f"{obj.name}_{suffix}", baked_mesh)
    baked_obj.matrix_world = obj.matrix_world.copy()
    _link_object_to_context_collection(context, baked_obj)
    return baked_obj


class PRIG_OT_bake_grid(bpy.types.Operator):
    bl_idname = "prig.bake_grid"
    bl_label = "Bake Grid"

    def execute(self, context):
        root = _active_rig_root(context)
        if not root:
            self.report({'ERROR'}, "Active rig root not found")
            return {'CANCELLED'}

        grid_name = root.get("prig_grid_obj")
        grid = bpy.data.objects.get(grid_name)
        if not grid:
            self.report({'ERROR'}, "Grid object not found")
            return {'CANCELLED'}

        baked = _bake_object(context, grid, "BAKED")
        self.report({'INFO'}, f"Grid baked: {baked.name}")
        return {'FINISHED'}


class PRIG_OT_bake_target(bpy.types.Operator):
    bl_idname = "prig.bake_target"
    bl_label = "Bake Target"

    def execute(self, context):
        root = _active_rig_root(context)
        if not root:
            self.report({'ERROR'}, "Active rig root not found")
            return {'CANCELLED'}

        target_names = json.loads(root.get("prig_target_objs", "[]"))
        targets = [bpy.data.objects.get(name) for name in target_names]
        targets = [t for t in targets if t]
        if not targets:
            self.report({'ERROR'}, "No target objects found")
            return {'CANCELLED'}

        baked_names = []
        for target in targets:
            baked = _bake_object(context, target, "BAKED")
            baked_names.append(baked.name)

        self.report({'INFO'}, "Target baked: " + ", ".join(baked_names))
        return {'FINISHED'}


CLASSES = (PRIG_OT_bake_grid, PRIG_OT_bake_target)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
