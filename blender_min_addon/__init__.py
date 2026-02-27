bl_info = {
    "name": "Cross_obj",
    "author": "Codex",
    "version": (0, 2, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Minimal",
    "description": "Create an intersection model from 2 or more selected mesh/curve objects.",
    "category": "Object",
}

import bpy

SUPPORTED_TYPES = {'MESH', 'CURVE', 'SURFACE', 'FONT'}


def _object_to_world_mesh(context, obj):
    depsgraph = context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(obj_eval, depsgraph=depsgraph)
    mesh.transform(obj.matrix_world)
    return mesh


def _apply_intersect_modifier(base_obj, cutter_obj, context):
    depsgraph = context.evaluated_depsgraph_get()

    mod = base_obj.modifiers.new(name="Intersect", type='BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.solver = 'EXACT'
    mod.object = cutter_obj

    evaluated = base_obj.evaluated_get(depsgraph)
    new_mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)

    base_obj.modifiers.remove(mod)
    old_mesh = base_obj.data
    base_obj.data = new_mesh
    bpy.data.meshes.remove(old_mesh)


class MINIMAL_OT_build_intersection(bpy.types.Operator):
    """Build one mesh from the intersecting area of 2+ selected objects"""

    bl_idname = "minimal.build_intersection"
    bl_label = "交差モデルを作成"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type in SUPPORTED_TYPES]

        if len(selected) < 2:
            self.report({'ERROR'}, "MESH/CURVE などを2つ以上選択してください。")
            return {'CANCELLED'}

        collection = context.collection or context.scene.collection
        temp_objects = []

        try:
            for src in selected:
                mesh = _object_to_world_mesh(context, src)
                temp = bpy.data.objects.new(f"_tmp_{src.name}", mesh)
                collection.objects.link(temp)
                temp_objects.append(temp)

            result_obj = temp_objects[0]
            result_obj.name = "Intersection_Result"

            for cutter in temp_objects[1:]:
                _apply_intersect_modifier(result_obj, cutter, context)

            for tmp in temp_objects[1:]:
                mesh = tmp.data
                bpy.data.objects.remove(tmp, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

            if len(result_obj.data.polygons) == 0:
                self.report({'WARNING'}, "交差領域が見つかりませんでした。")
            else:
                self.report({'INFO'}, "交差モデルを作成しました。")

            for obj in context.selected_objects:
                obj.select_set(False)
            result_obj.select_set(True)
            context.view_layer.objects.active = result_obj

            return {'FINISHED'}

        except RuntimeError as exc:
            self.report({'ERROR'}, f"処理に失敗しました: {exc}")
            for tmp in temp_objects:
                if tmp.name in bpy.data.objects:
                    mesh = tmp.data
                    bpy.data.objects.remove(tmp, do_unlink=True)
                    if mesh.users == 0:
                        bpy.data.meshes.remove(mesh)
            return {'CANCELLED'}


class MINIMAL_PT_panel(bpy.types.Panel):
    bl_label = "Cross_obj"
    bl_idname = "MINIMAL_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cross_obj'

    def draw(self, context):
        layout = self.layout
        layout.label(text="2つ以上を選択して実行")
        layout.operator(MINIMAL_OT_build_intersection.bl_idname, icon='MOD_BOOLEAN')


classes = (
    MINIMAL_OT_build_intersection,
    MINIMAL_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
