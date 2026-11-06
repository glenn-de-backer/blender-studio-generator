# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent per-studio parameters and their live update callbacks."""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
)

from .constants import PRESETS
from .core.lighting import LIGHTING_PRESETS, RIM_POSITIONS, update_lighting
from .core.mesh_builder import rebuild


# -------------------------------------------------------------
# Property Update Callbacks
# -------------------------------------------------------------
def update_geometry(self, context):
    """Rebuild mesh geometry and update lighting for the owning object."""
    studio_object = self.id_data
    if isinstance(studio_object, bpy.types.Object) and self.enabled:
        rebuild(studio_object)


def update_light_settings(self, context):
    """Update only light rig parameters without triggering a mesh rebuild."""
    studio_object = self.id_data
    if isinstance(studio_object, bpy.types.Object) and self.enabled:
        update_lighting(studio_object)


# -------------------------------------------------------------
# Property Group Definition
# -------------------------------------------------------------
class StudioSettings(bpy.types.PropertyGroup):
    """Stored on bpy.types.Object to give each studio independent settings."""

    # Master activation toggle
    enabled: BoolProperty(
        name='Enabled',
        default=False,
        options=set(),
    )

    # ---------------------------------------------------------
    # 1. Geometry & Cyclorama Dimensions
    # ---------------------------------------------------------
    preset: EnumProperty(
        name='Shape',
        items=PRESETS,
        default='L',
        update=update_geometry,
        options=set(),
    )
    corner_side: EnumProperty(
        name='Corner Side',
        description='Placement side for the corner cyclorama wall',
        items=[
            ('LEFT', 'Left', 'Wall on the left'),
            ('RIGHT', 'Right', 'Wall on the right'),
        ],
        default='LEFT',
        update=update_geometry,
        options=set(),
    )
    width: FloatProperty(
        name='Width',
        default=6.0,
        min=0.1,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )
    depth: FloatProperty(
        name='Depth',
        default=6.0,
        min=0.1,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )
    height: FloatProperty(
        name='Wall Height',
        default=4.0,
        min=0.1,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )
    radius: FloatProperty(
        name='Floor Curve Radius',
        default=1.0,
        min=0.01,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )
    second_radius: FloatProperty(
        name='Second Curve Radius',
        default=0.5,
        min=0.01,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )
    ceiling: FloatProperty(
        name='Ceiling Reach',
        default=3.0,
        min=0.05,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )
    drop: FloatProperty(
        name='Front Drop',
        default=1.0,
        min=0.05,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )
    segments: IntProperty(
        name='Curve Segments',
        default=24,
        min=3,
        max=128,
        update=update_geometry,
        options=set(),
    )
    thickness: FloatProperty(
        name='Thickness',
        default=0.02,
        min=0.0,
        max=1.0,
        unit='LENGTH',
        update=update_geometry,
        options=set(),
    )

    # ---------------------------------------------------------
    # 2. Master & Global Lighting Controls
    # ---------------------------------------------------------
    # NONE is default: creating a studio never injects lights unless requested
    lighting_preset: EnumProperty(
        name='Lighting Setup',
        items=LIGHTING_PRESETS,
        default='NONE',
        update=update_light_settings,
        options=set(),
    )
    light_power: FloatProperty(
        name='Main Power (W)',
        description='Base power value scaled across individual lamps by preset ratios',
        default=1000.0,
        min=0.0,
        soft_max=5000.0,
        update=update_light_settings,
        options=set(),
    )
    light_size: FloatProperty(
        name='Softbox Size',
        description='Base diameter scaled across individual lamps by preset ratios',
        default=2.0,
        min=0.01,
        unit='LENGTH',
        update=update_light_settings,
        options=set(),
    )
    light_distance: FloatProperty(
        name='Horizontal Spread',
        description='Relative horizontal offset scalar from the studio center',
        default=1.0,
        min=0.2,
        max=1.1,
        update=update_light_settings,
        options=set(),
    )
    light_color: FloatVectorProperty(
        name='Overall Tint',
        description='Global multiplier tint applied across all light colors',
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_light_settings,
        options=set(),
    )

    # ---------------------------------------------------------
    # 3. Individual Light Controls (Power, Color, Enable, Position)
    # ---------------------------------------------------------
    # Key Light
    key_light_power: FloatProperty(
        name='Key Power (W)',
        default=1000.0,
        min=0.0,
        soft_max=5000.0,
        update=update_light_settings,
        options=set(),
    )
    key_light_color: FloatVectorProperty(
        name='Key Color',
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_light_settings,
        options=set(),
    )
    key_light_enabled: BoolProperty(
        name='Key Enabled',
        default=True,
        update=update_light_settings,
        options=set(),
    )

    # Fill Light
    fill_light_power: FloatProperty(
        name='Fill Power (W)',
        default=450.0,
        min=0.0,
        soft_max=5000.0,
        update=update_light_settings,
        options=set(),
    )
    fill_light_color: FloatVectorProperty(
        name='Fill Color',
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_light_settings,
        options=set(),
    )
    fill_light_enabled: BoolProperty(
        name='Fill Enabled',
        default=True,
        update=update_light_settings,
        options=set(),
    )

    # Rim Light
    rim_position: EnumProperty(
        name='Rim Position',
        description='Horizontal placement of the rim / backlight',
        items=RIM_POSITIONS,
        default='BACK_RIGHT',
        update=update_light_settings,
        options=set(),
    )
    rim_light_power: FloatProperty(
        name='Rim Power (W)',
        default=750.0,
        min=0.0,
        soft_max=5000.0,
        update=update_light_settings,
        options=set(),
    )
    rim_light_color: FloatVectorProperty(
        name='Rim Color',
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_light_settings,
        options=set(),
    )
    rim_light_enabled: BoolProperty(
        name='Rim Enabled',
        default=True,
        update=update_light_settings,
        options=set(),
    )

    # Top / Overhead Light
    top_light_power: FloatProperty(
        name='Top Power (W)',
        default=1000.0,
        min=0.0,
        soft_max=5000.0,
        update=update_light_settings,
        options=set(),
    )
    top_light_color: FloatVectorProperty(
        name='Top Color',
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_light_settings,
        options=set(),
    )
    top_light_enabled: BoolProperty(
        name='Top Enabled',
        default=True,
        update=update_light_settings,
        options=set(),
    )

    # Front Fill Light
    front_fill_light_power: FloatProperty(
        name='Front Fill Power (W)',
        default=250.0,
        min=0.0,
        soft_max=5000.0,
        update=update_light_settings,
        options=set(),
    )
    front_fill_light_color: FloatVectorProperty(
        name='Front Fill Color',
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_light_settings,
        options=set(),
    )
    front_fill_light_enabled: BoolProperty(
        name='Front Fill Enabled',
        default=True,
        update=update_light_settings,
        options=set(),
    )

    # ---------------------------------------------------------
    # 4. UI Accordion & Disclosure States
    # ---------------------------------------------------------
    key_light_expanded: BoolProperty(
        name='Show Key Settings',
        default=False,
        options=set(),
    )
    fill_light_expanded: BoolProperty(
        name='Show Fill Settings',
        default=False,
        options=set(),
    )
    rim_light_expanded: BoolProperty(
        name='Show Rim Settings',
        default=False,
        options=set(),
    )
    top_light_expanded: BoolProperty(
        name='Show Top Settings',
        default=False,
        options=set(),
    )
    front_fill_light_expanded: BoolProperty(
        name='Show Front Fill Settings',
        default=False,
        options=set(),
    )

    # ---------------------------------------------------------
    # 5. Internal State & Migration Flags
    # ---------------------------------------------------------
    individual_power_initialized: BoolProperty(
        default=False,
        options={'HIDDEN'},
    )
    initializing_light_power: BoolProperty(
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )