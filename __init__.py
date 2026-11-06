# SPDX-License-Identifier: GPL-3.0-or-later
"""Studio Generator entry point: registration and integration with Blender UI."""

import importlib
import sys
import bpy
from bpy.props import PointerProperty

# If reloading or re-enabling in the same Blender session, force-reload submodules
if "operators" in locals():
    importlib.reload(constants)
    if "core.lighting" in sys.modules:
        importlib.reload(sys.modules["core.lighting"])
    if "core.geometry" in sys.modules:
        importlib.reload(sys.modules["core.geometry"])
    if "core.mesh_builder" in sys.modules:
        importlib.reload(sys.modules["core.mesh_builder"])
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(ui)

from . import constants, properties, operators, ui
from .operators import (
    STUDIO_OT_add,
    STUDIO_OT_bake,
    STUDIO_OT_rebuild,
    STUDIO_OT_refresh_lighting,
)
from .properties import StudioSettings
from .ui import STUDIO_PT_panel, menu

CLASSES = (
    StudioSettings,
    STUDIO_OT_add,
    STUDIO_OT_rebuild,
    STUDIO_OT_bake,
    STUDIO_OT_refresh_lighting,
    STUDIO_PT_panel,
)


def register():
    """Register classes, bind custom properties, and attach UI menu entries."""
    for registered_class in CLASSES:
        bpy.utils.register_class(registered_class)

    # Attach parametric settings container to the Blender Object data block
    bpy.types.Object.studio_settings = PointerProperty(type=StudioSettings)

    # Inject 'Studio Backdrop' operator menu into the Add > Mesh popup menu
    bpy.types.VIEW3D_MT_mesh_add.append(menu)

    # Force immediate redraw of all active 3D viewports
    def force_redraw():
        wm = getattr(bpy.context, "window_manager", None)
        if not wm:
            return None
        for window in wm.windows:
            screen = getattr(window, "screen", None)
            if screen:
                for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
        return None

    # Run redraw directly and schedule a deferred timer for extension hot-loads
    force_redraw()
    if not bpy.app.background:
        bpy.app.timers.register(force_redraw, first_interval=0.05)


def unregister():
    """Detach UI menu entries, unbind properties, and safely unregister classes."""
    try:
        bpy.types.VIEW3D_MT_mesh_add.remove(menu)
    except Exception:
        pass

    if hasattr(bpy.types.Object, 'studio_settings'):
        del bpy.types.Object.studio_settings

    for registered_class in reversed(CLASSES):
        if hasattr(registered_class, 'bl_rna'):
            try:
                bpy.utils.unregister_class(registered_class)
            except RuntimeError:
                pass

    # Tag redraw to remove tabs cleanly
    wm = getattr(bpy.context, "window_manager", None)
    if wm:
        for window in wm.windows:
            screen = getattr(window, "screen", None)
            if screen:
                for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
