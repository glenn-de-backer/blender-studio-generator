# SPDX-License-Identifier: GPL-3.0-or-later
"""Studio Generator entry point: registration and integration with Blender UI."""

import bpy
from bpy.props import PointerProperty

from .operators import (
    STUDIO_OT_add,
    STUDIO_OT_bake,
    STUDIO_OT_rebuild,
    STUDIO_OT_refresh_lighting,
)
from .properties import StudioSettings
from .ui import STUDIO_PT_panel, menu

# -------------------------------------------------------------
# Add-on Metadata
# -------------------------------------------------------------
bl_info = {
    'name': 'Simple Studio Generator',
    'author': 'Glenn De Backer',
    'version': (1, 1, 0),
    'blender': (5, 0, 0),
    'category': 'Add Mesh',
    'location': 'View3D > Sidebar > Studio',
}

# Ordered class list for registration
CLASSES = (
    StudioSettings,
    STUDIO_OT_add,
    STUDIO_OT_rebuild,
    STUDIO_OT_bake,
    STUDIO_OT_refresh_lighting,
    STUDIO_PT_panel,
)


# -------------------------------------------------------------
# Add-on Lifecycle Callbacks
# -------------------------------------------------------------
def register():
    """Register classes, bind custom properties, and attach UI menu entries."""
    # Property groups must be registered prior to panels and operators using them
    for registered_class in CLASSES:
        bpy.utils.register_class(registered_class)

    # Attach parametric settings container to the Blender Object data block
    bpy.types.Object.studio_settings = PointerProperty(type=StudioSettings)

    # Inject 'Studio Backdrop' operator menu into the Add > Mesh popup menu
    bpy.types.VIEW3D_MT_mesh_add.append(menu)


def unregister():
    """Detach UI menu entries, unbind properties, and unregister classes."""
    # Remove operator item from the Add > Mesh menu
    bpy.types.VIEW3D_MT_mesh_add.remove(menu)

    # Clean up custom property from the Object data block
    del bpy.types.Object.studio_settings

    # Unregister classes in reverse dependency order to prevent reference errors
    for registered_class in reversed(CLASSES):
        bpy.utils.unregister_class(registered_class)