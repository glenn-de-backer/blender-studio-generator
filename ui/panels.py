# SPDX-License-Identifier: GPL-3.0-or-later
"""Studio sidebar layout. Geometry and light logic live in other modules."""

import bpy
from ..core.lighting import (
    LIGHT_COLOR_PROPERTIES,
    LIGHT_ENABLED_PROPERTIES,
    LIGHT_POWER_PROPERTIES,
    PRESET_LIGHT_ROLES,
)


class STUDIO_PT_panel(bpy.types.Panel):
    """UI Panel in the 3D Viewport sidebar for generating and editing studios."""

    bl_label = 'Studio Generator'
    bl_idname = 'STUDIO_PT_generator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Studio'

    def draw(self, context):
        layout = self.layout

        # Operator menu to spawn a new studio preset
        layout.operator_menu_enum(
            'mesh.add_parametric_studio',
            'preset',
            text='Add Studio',
            icon='ADD',
        )

        # Ensure an active mesh object with studio settings is selected
        studio_object = context.object
        if (
            not studio_object
            or studio_object.type != 'MESH'
            or not studio_object.studio_settings.enabled
        ):
            layout.label(text='Select a generated studio to edit.')
            return

        settings = studio_object.studio_settings

        # Lock controls to Object Mode to avoid mesh edit conflicts
        controls = layout.column()
        controls.enabled = studio_object.mode == 'OBJECT'

        # -------------------------------------------------------------
        # 1. Base Dimensions & Geometry Settings
        # -------------------------------------------------------------
        for property_name in ('preset', 'width', 'depth', 'height', 'radius'):
            controls.prop(settings, property_name)

        # Preset-specific geometry controls
        if settings.preset == 'CORNER':
            controls.prop(settings, 'corner_side')

        if settings.preset in {'S', 'C'}:
            controls.prop(settings, 'second_radius')
            controls.prop(settings, 'drop' if settings.preset == 'S' else 'ceiling')

        controls.prop(settings, 'segments')
        controls.prop(settings, 'thickness')

        # -------------------------------------------------------------
        # 2. Clamped / Fitted Radius Information
        # -------------------------------------------------------------
        fitted_floor_radius = min(
            settings.radius,
            settings.depth * 0.24,
            settings.height * 0.24,
            settings.width * 0.24,
        )
        if fitted_floor_radius < settings.radius - 1e-6:
            controls.label(
                text=f'Fitted floor radius: {fitted_floor_radius:.3f}',
                icon='INFO',
            )

        if settings.preset in {'S', 'C'}:
            secondary_boundary = settings.ceiling if settings.preset == 'C' else settings.drop
            fitted_secondary_radius = min(
                settings.second_radius,
                settings.depth * 0.24,
                settings.height * 0.24,
                secondary_boundary * 0.8,
            )
            if fitted_secondary_radius < settings.second_radius - 1e-6:
                controls.label(
                    text=f'Fitted second radius: {fitted_secondary_radius:.3f}',
                    icon='INFO',
                )

        # -------------------------------------------------------------
        # 3. Quick Material Controls (Principled BSDF)
        # -------------------------------------------------------------
        active_mat = studio_object.active_material
        if active_mat and active_mat.use_nodes:
            principled_shader = next(
                (n for n in active_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'),
                None,
            )
            if principled_shader:
                controls.prop(
                    principled_shader.inputs['Base Color'],
                    'default_value',
                    text='Color',
                )
                controls.prop(
                    principled_shader.inputs['Roughness'],
                    'default_value',
                    text='Roughness',
                )

        # -------------------------------------------------------------
        # 4. Optional Lighting Rig
        # -------------------------------------------------------------
        lighting_box = controls.box()
        lighting_box.label(text='Optional Lighting', icon='LIGHT_AREA')
        lighting_box.prop(settings, 'lighting_preset')

        if settings.lighting_preset != 'NONE':
            for property_name in ('light_size', 'light_distance', 'light_color'):
                lighting_box.prop(settings, property_name)

            # Show only the lamps required by the selected preset
            light_colors = lighting_box.column(align=True)
            light_colors.label(text='Individual Lights')

            for role in PRESET_LIGHT_ROLES[settings.lighting_preset]:
                light_box = light_colors.box()

                # Property name controlling whether this specific sub-box is expanded
                expansion_property = LIGHT_COLOR_PROPERTIES[role].replace('_color', '_expanded')
                is_expanded = getattr(settings, expansion_property)

                # Collapsible header row with toggle arrow and enable/disable checkbox
                light_header = light_box.row(align=True)
                light_header.prop(
                    settings,
                    expansion_property,
                    text=role,
                    icon='TRIA_DOWN' if is_expanded else 'TRIA_RIGHT',
                    emboss=False,
                )
                light_header.prop(settings, LIGHT_ENABLED_PROPERTIES[role], text='')

                # Expanded light parameters (power and tint)
                if is_expanded:
                    light_controls = light_box.column()
                    light_controls.enabled = getattr(settings, LIGHT_ENABLED_PROPERTIES[role])
                    light_controls.prop(
                        settings,
                        LIGHT_POWER_PROPERTIES[role],
                        text='Power (W)',
                    )
                    light_controls.prop(
                        settings,
                        LIGHT_COLOR_PROPERTIES[role],
                        text='Color',
                    )

            lighting_box.operator('object.refresh_studio_lighting', icon='FILE_REFRESH')
            lighting_box.label(text='Choose None to remove this rig.')

        # -------------------------------------------------------------
        # 5. Studio Action Operators
        # -------------------------------------------------------------
        controls.operator('object.rebuild_parametric_studio', icon='FILE_REFRESH')
        controls.operator('object.bake_parametric_studio', icon='MESH_DATA')

        if studio_object.mode != 'OBJECT':
            layout.label(text='Return to Object Mode to adjust.')


def menu(self, context):
    """Entry point helper for appending to the 3D Viewport Add > Mesh menu."""
    self.layout.operator_menu_enum(
        'mesh.add_parametric_studio',
        'preset',
        text='Studio Backdrop',
    )