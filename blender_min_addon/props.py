import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
)

SUPPORTED_SURFACE_TYPES = {'MESH'}
SUPPORTED_CURVE_TYPES = {'CURVE'}
SUPPORTED_TARGET_TYPES = {'MESH'}


def _poll_surface(_self, obj):
    return obj is not None and obj.type in SUPPORTED_SURFACE_TYPES


def _poll_curve(_self, obj):
    return obj is not None and obj.type in SUPPORTED_CURVE_TYPES


def _poll_target(_self, obj):
    return obj is not None and obj.type in SUPPORTED_TARGET_TYPES


class PRIG_Settings(bpy.types.PropertyGroup):
    reference_surface: PointerProperty(name="Reference Surface", type=bpy.types.Object, poll=_poll_surface)
    control_curve_a: PointerProperty(name="Curve A", type=bpy.types.Object, poll=_poll_curve)
    control_curve_b: PointerProperty(name="Curve B", type=bpy.types.Object, poll=_poll_curve)
    control_curve_c: PointerProperty(name="Curve C", type=bpy.types.Object, poll=_poll_curve)
    target_a: PointerProperty(name="Target A", type=bpy.types.Object, poll=_poll_target)
    target_b: PointerProperty(name="Target B", type=bpy.types.Object, poll=_poll_target)
    target_c: PointerProperty(name="Target C", type=bpy.types.Object, poll=_poll_target)

    grid_resolution_u: IntProperty(name="Grid U", default=64, min=16, max=256)
    grid_resolution_v: IntProperty(name="Grid V", default=64, min=16, max=256)

    projection_method: EnumProperty(
        name="Projection Method",
        items=[
            ('SURFACE_NORMAL', "Surface Normal", "Project along surface normal"),
            ('CUSTOM_VECTOR', "Custom Vector", "Project along custom vector"),
            ('OBJECT_AXIS', "Object Axis", "Project along object axis"),
        ],
        default='SURFACE_NORMAL',
    )
    custom_vector: bpy.props.FloatVectorProperty(name="Custom Vector", default=(0.0, 0.0, 1.0), subtype='XYZ')

    influence_radius: FloatProperty(name="Influence Radius", default=1.0, min=0.001)
    falloff_type: EnumProperty(
        name="Falloff",
        items=[('SMOOTH', "Smooth", ""), ('SHARP', "Sharp", ""), ('LINEAR', "Linear", "")],
        default='SMOOTH',
    )
    pin_borders: BoolProperty(name="Pin Borders", default=False)
    live_update: BoolProperty(name="Live Update", default=True)
    update_throttle_ms: IntProperty(name="Update Throttle (ms)", default=66, min=16, max=1000)

    displacement_strength: FloatProperty(name="Displacement Strength", default=1.0)
    clamp: FloatProperty(name="Clamp", default=10.0, min=0.0)


CLASSES = (PRIG_Settings,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.prig_settings = PointerProperty(type=PRIG_Settings)


def unregister():
    del bpy.types.Scene.prig_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
