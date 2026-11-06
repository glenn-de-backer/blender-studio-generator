# SPDX-License-Identifier: GPL-3.0-or-later
"""Undoable actions exposed in the Studio panel and Add menu."""

import bpy
from bpy.props import EnumProperty

from ..constants import PRESETS
from ..core.lighting import reset_lighting_defaults
from ..core.mesh_builder import rebuild


class STUDIO_OT_add(bpy.types.Operator):
    """Instantiate a new procedural studio backdrop object in the active scene."""

    bl_idname = 'mesh.add_parametric_studio'
    bl_label = 'Add Studio'
    bl_options = {'REGISTER', 'UNDO'}

    preset: EnumProperty(
        name='Preset',
        items=PRESETS,
        default='L',
    )

    @classmethod
    def poll(cls, context):
        # Prevent spawning meshes while in edit or pose modes
        return context.mode == 'OBJECT'

    def execute(self, context):
        # -------------------------------------------------------------
        # 1. Instantiate Object and Mesh Data
        # -------------------------------------------------------------
        studio_mesh = bpy.data.meshes.new('Studio Surface')
        object_name = f'Studio {self.preset.title()}'
        studio_object = bpy.data.objects.new(object_name, studio_mesh)

        # Link into the active collection and position at the 3D cursor
        context.collection.objects.link(studio_object)
        studio_object.location = context.scene.cursor.location

        # -------------------------------------------------------------
        # 2. Selection and Active State Management
        # -------------------------------------------------------------
        for selected_object in context.selected_objects:
            selected_object.select_set(False)

        studio_object.select_set(True)
        context.view_layer.objects.active = studio_object

        # -------------------------------------------------------------
        # 3. Procedural Parameters & Initial Mesh Generation
        # -------------------------------------------------------------
        studio_object.studio_settings.preset = self.preset
        studio_object.studio_settings.enabled = True
        rebuild(studio_object)

        # -------------------------------------------------------------
        # 4. Default Material Setup (Principled BSDF Matte)
        # -------------------------------------------------------------
        material = bpy.data.materials.new('Studio Matte')
        material.use_nodes = True

        principled_shader = material.node_tree.nodes.get('Principled BSDF')
        if principled_shader:
            # 80% neutral gray base color, 0.8 roughness for diffused reflections
            principled_shader.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
            principled_shader.inputs['Roughness'].default_value = 0.8

        studio_object.data.materials.append(material)

        return {'FINISHED'}


class STUDIO_OT_rebuild(bpy.types.Operator):
    """Regenerate the selected studio from its saved procedural settings."""

    bl_idname = 'object.rebuild_parametric_studio'
    bl_label = 'Rebuild Studio'
    bl_description = (
        'Regenerate the studio mesh and reset its generated lighting from the current settings. '
        'Preserves object transforms and material slots, but replaces manual vertex edits, '
        'UV edits and per-face material assignments. Use Make Editable Mesh before manual modeling'
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Requires an active mesh object with parametric studio settings enabled in Object Mode
        studio_object = context.object
        return (
            studio_object is not None
            and studio_object.type == 'MESH'
            and studio_object.mode == 'OBJECT'
            and studio_object.studio_settings.enabled
        )

    def execute(self, context):
        # Re-run procedural mesh and lighting generation logic
        rebuild(context.object)
        return {'FINISHED'}


class STUDIO_OT_bake(bpy.types.Operator):
    """Bake procedural studio to a standard editable mesh."""

    bl_idname = 'object.bake_parametric_studio'
    bl_label = 'Make Editable Mesh'
    bl_description = 'Stop procedural updates; keep the mesh and modifiers for manual editing'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Uses identical validation constraints as the rebuild operator
        return STUDIO_OT_rebuild.poll(context)

    def execute(self, context):
        # Sever procedural sync by disabling the studio flag
        context.object.studio_settings.enabled = False
        return {'FINISHED'}


class STUDIO_OT_refresh_lighting(bpy.types.Operator):
    """Restore default lighting settings for the currently selected setup."""

    bl_idname = 'object.refresh_studio_lighting'
    bl_label = 'Reset Lighting to Defaults'
    bl_description = (
        'Reset all light powers, colors, enabled states, size and spread; '
        'keep the selected setup and studio dimensions'
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Valid only when an active procedural studio is selected
        return STUDIO_OT_rebuild.poll(context)

    def execute(self, context):
        # Reset light properties while preserving the active studio preset
        reset_lighting_defaults(context.object)
        return {'FINISHED'}