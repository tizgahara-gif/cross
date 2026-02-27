bl_info = {
    "name": "Projection Rig",
    "author": "Codex",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Projection Rig",
    "description": "Auto-build projection rigs from curves and reference surfaces.",
    "category": "Object",
}

from . import props
from .operators import create_rig, bake, diagnostics
from .ui import panel

MODULES = (props, create_rig, bake, diagnostics, panel)


def register():
    for mod in MODULES:
        mod.register()


def unregister():
    for mod in reversed(MODULES):
        mod.unregister()


if __name__ == "__main__":
    register()
