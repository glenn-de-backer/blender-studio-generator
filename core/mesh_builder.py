# SPDX-License-Identifier: GPL-3.0-or-later
"""Build Blender mesh data and update the thickness modifier."""

import bmesh
import bpy

from .geometry import geometry
from .lighting import update_lighting


def rebuild(studio_object):
    """Replace generated mesh data while preserving materials and transforms."""
    settings = studio_object.studio_settings

    # Validate state: must be an enabled studio mesh in Object Mode
    if (
        not settings.enabled
        or studio_object.type != 'MESH'
        or studio_object.mode != 'OBJECT'
    ):
        return

    # -------------------------------------------------------------
    # 1. Generate Raw Mesh from Geometry Data
    # -------------------------------------------------------------
    vertices, faces = geometry(settings)
    new_mesh = bpy.data.meshes.new('Studio Surface')
    new_mesh.from_pydata(vertices, [], faces)
    new_mesh.update()

    # -------------------------------------------------------------
    # 2. Consistent Inward Normal Orientation via BMesh
    # -------------------------------------------------------------
    # Ensure all connected faces point toward the studio interior
    editable_mesh = bmesh.new()
    editable_mesh.from_mesh(new_mesh)
    bmesh.ops.recalc_face_normals(editable_mesh, faces=list(editable_mesh.faces))

    # Identify a horizontal floor face (Z ≈ 0) to verify vertical normal orientation
    floor_face = next(
        (
            face for face in editable_mesh.faces
            if all(abs(vertex.co.z) < 1e-7 for vertex in face.verts)
        ),
        None,
    )

    # If the floor faces downward, invert the entire mesh to orient inward
    if floor_face and floor_face.normal.z < 0:
        bmesh.ops.reverse_faces(editable_mesh, faces=list(editable_mesh.faces))

    editable_mesh.to_mesh(new_mesh)
    editable_mesh.free()

    # Enable smooth shading across all polygons
    for face in new_mesh.polygons:
        face.use_smooth = True

    # -------------------------------------------------------------
    # 3. Planar UV Map Projection
    # -------------------------------------------------------------
    uv_layer = new_mesh.uv_layers.new(name='Studio UV')
    max_dimension = max(settings.depth, settings.height)

    for loop in new_mesh.loops:
        coords = new_mesh.vertices[loop.vertex_index].co
        u = (coords.x / settings.width) + 0.5
        v = ((coords.y + coords.z) / max_dimension) + 0.5
        uv_layer.data[loop.index].uv = (u, v)

    # -------------------------------------------------------------
    # 4. Swap Mesh Data & Retain Material Assignments
    # -------------------------------------------------------------
    previous_mesh = studio_object.data
    for material in previous_mesh.materials:
        new_mesh.materials.append(material)

    studio_object.data = new_mesh

    # Clean up the old mesh data block if no other objects share it
    if previous_mesh.users == 0:
        bpy.data.meshes.remove(previous_mesh)

    # -------------------------------------------------------------
    # 5. Solidify Modifier Management
    # -------------------------------------------------------------
    thickness_modifier = next(
        (
            mod for mod in studio_object.modifiers
            if mod.type == 'SOLIDIFY' and mod.name == 'Studio Thickness'
        ),
        None,
    )

    if thickness_modifier is None:
        thickness_modifier = studio_object.modifiers.new(
            'Studio Thickness',
            'SOLIDIFY',
        )

    thickness_modifier.thickness = settings.thickness
    thickness_modifier.offset = -1  # Extrude outward/downward from front face
    thickness_modifier.show_viewport = settings.thickness > 0
    thickness_modifier.show_render = settings.thickness > 0

    # -------------------------------------------------------------
    # 6. Synchronize Lighting Rig
    # -------------------------------------------------------------
    # Re-align and scale parented lighting rigs to match the updated dimensions
    update_lighting(studio_object)