import bpy


class PRIG_PT_main(bpy.types.Panel):
    bl_label = "Projection Rig"
    bl_idname = "PRIG_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Projection Rig'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.prig_settings

        box = layout.box()
        box.label(text="Create Rig")
        box.prop(settings, "reference_surface")
        box.prop(settings, "control_curve_a")
        box.prop(settings, "control_curve_b")
        box.prop(settings, "control_curve_c")
        box.prop(settings, "target_a")
        box.prop(settings, "target_b")
        box.prop(settings, "target_c")
        row = box.row(align=True)
        row.prop(settings, "grid_resolution_u")
        row.prop(settings, "grid_resolution_v")
        box.prop(settings, "projection_method")
        if settings.projection_method == 'CUSTOM_VECTOR':
            box.prop(settings, "custom_vector")
        box.prop(settings, "influence_radius")
        box.prop(settings, "falloff_type")
        box.prop(settings, "pin_borders")
        box.operator("prig.create_rig", icon='OUTLINER_OB_EMPTY')

        box = layout.box()
        box.label(text="Update Rig")
        box.prop(settings, "live_update")
        box.prop(settings, "update_throttle_ms")
        row = box.row(align=True)
        row.operator("prig.update_rig", icon='FILE_REFRESH')
        row.operator("prig.select_rig_objects", icon='RESTRICT_SELECT_OFF')
        box.operator("prig.duplicate_rig", icon='DUPLICATE')

        box = layout.box()
        box.label(text="Bake")
        row = box.row(align=True)
        row.operator("prig.bake_grid", icon='MESH_GRID')
        row.operator("prig.bake_target", icon='MESH_DATA')

        box = layout.box()
        box.label(text="Diagnostics")
        box.operator("prig.diagnostics", icon='INFO')

        box = layout.box()
        box.label(text="Advanced")
        box.prop(settings, "displacement_strength")
        box.prop(settings, "clamp")


CLASSES = (PRIG_PT_main,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
