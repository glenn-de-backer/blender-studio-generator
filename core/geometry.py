# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure geometry generation, with no Blender API dependencies."""

import math


def geometry(settings):
    """Return welded surface coordinates and faces; radii constrained to fit.

    Generates parametric studio backdrops (cycloramas) across several preset shapes:
    - Linear extrusions along X (L-curve, S-curve, U-ramp, C-curve).
    - Curved sweeps in XY swept through Z (Corner cyc with spherical transition).
    """
    width = settings.width
    depth = settings.depth
    height = settings.height
    segment_count = settings.segments

    # -------------------------------------------------------------
    # 1. Radius Constraints
    # -------------------------------------------------------------
    # Fit bends within bounds to prevent self-intersecting or overlapping geometry.
    floor_radius = min(
        settings.radius,
        depth * 0.24,
        height * 0.24,
        width * 0.24,
    )

    secondary_limit = (settings.ceiling if settings.preset == 'C' else settings.drop) * 0.8
    secondary_radius = min(
        settings.second_radius,
        depth * 0.24,
        height * 0.24,
        secondary_limit,
    )

    vertices = []
    faces = []
    vertex_lookup = {}

    # -------------------------------------------------------------
    # 2. Vertex Welding and Patch Generation Helpers
    # -------------------------------------------------------------
    def get_vertex_index(coordinates):
        """Register or retrieve a coordinate index, welding proximate points."""
        # Rounded coordinates weld adjoining patches and collapse polar fan points.
        coordinate_key = tuple(round(coord, 9) for coord in coordinates)
        if coordinate_key not in vertex_lookup:
            vertex_lookup[coordinate_key] = len(vertices)
            vertices.append(coordinates)
        return vertex_lookup[coordinate_key]

    def append_surface_patch(rows):
        """Construct quad and tri faces from a 2D grid array of coordinates."""
        vertex_rows = [
            [get_vertex_index(coord) for coord in row]
            for row in rows
        ]

        for current_row, next_row in zip(vertex_rows, vertex_rows[1:]):
            for col in range(len(current_row) - 1):
                # Using dict.fromkeys deduplicates collapsed vertices (e.g. quad -> tri)
                # while preserving winding order.
                face = list(dict.fromkeys((
                    current_row[col],
                    current_row[col + 1],
                    next_row[col + 1],
                    next_row[col],
                )))
                if len(face) >= 3:
                    faces.append(face)

    # -------------------------------------------------------------
    # 3. Profile Construction (Linear Presets: L, S, U, C)
    # -------------------------------------------------------------
    if settings.preset != 'CORNER':
        # YZ cross-section to be extruded across the X axis. Front is negative Y.
        profile = []

        if settings.preset == 'S':
            # Dropdown front lip leading up into the floor
            profile.append((-depth / 2, -settings.drop))
            for i in range(segment_count + 1):
                angle = (math.pi / 2) * (i / segment_count)
                profile.append((
                    -depth / 2 + secondary_radius * (1 - math.cos(angle)),
                    -secondary_radius + secondary_radius * math.sin(angle),
                ))

        elif settings.preset == 'U':
            # Front raised rim curving down to the floor
            profile.append((-depth / 2, height))
            for i in range(segment_count + 1):
                angle = (math.pi / 2) * (i / segment_count)
                profile.append((
                    -depth / 2 + floor_radius * (1 - math.cos(angle)),
                    floor_radius * (1 - math.sin(angle)),
                ))

        else:
            # Standard flat floor leading from the front edge
            profile.append((-depth / 2, 0.0))

        # Primary floor-to-wall upward cove bend
        for i in range(segment_count + 1):
            angle = (math.pi / 2) * (i / segment_count)
            profile.append((
                depth / 2 - floor_radius + floor_radius * math.sin(angle),
                floor_radius * (1 - math.cos(angle)),
            ))

        if settings.preset == 'C':
            # Wall-to-ceiling curved cove and top return plane
            for i in range(segment_count + 1):
                angle = (math.pi / 2) * (i / segment_count)
                profile.append((
                    depth / 2 - secondary_radius + secondary_radius * math.cos(angle),
                    height - secondary_radius + secondary_radius * math.sin(angle),
                ))
            profile.append((depth / 2 - settings.ceiling, height))
        else:
            # Straight vertical back wall up to top edge
            profile.append((depth / 2, height))

        # Extrude the 2D profile symmetrically across the X axis
        extrude_rows = [
            [(x, y, z) for y, z in profile]
            for x in (-width / 2, width / 2)
        ]
        append_surface_patch(extrude_rows)

    # -------------------------------------------------------------
    # 4. Corner Cyc Construction
    # -------------------------------------------------------------
    else:
        # Sweeps a quarter-circle cove curve along an L-shaped plan path with a rounded corner.
        # At the floor level, the corner collapses to a single welded pole vertex,
        # forming a seamless spherical octant with a triangular fan.
        corner_center_x = -width / 2 + floor_radius
        corner_center_y = depth / 2 - floor_radius

        # Path format: (x, y, normal_inward_x, normal_inward_y)
        path = [(width / 2, depth / 2, 0.0, -1.0)]

        # Rounded corner arc on the XY plan
        for i in range(segment_count + 1):
            angle = (math.pi / 2) + (math.pi / 2) * (i / segment_count)
            path.append((
                corner_center_x + floor_radius * math.cos(angle),
                corner_center_y + floor_radius * math.sin(angle),
                -math.cos(angle),
                -math.sin(angle),
            ))

        path.append((-width / 2, -depth / 2, 1.0, 0.0))

        # Sweep the floor cove curve vertically up the path
        rows = []
        for i in range(segment_count + 1):
            angle = (math.pi / 2) * (i / segment_count)
            inset = floor_radius * (1 - math.sin(angle))
            z = floor_radius * (1 - math.cos(angle))
            rows.append([
                (x + inward_x * inset, y + inward_y * inset, z)
                for x, y, inward_x, inward_y in path
            ])

        # Top wall boundary rim
        rows.append([(x, y, height) for x, y, _, _ in path])
        append_surface_patch(rows)

        # Flat floor patch filling the interior corner floor space
        floor_patch = [
            [
                (corner_center_x, -depth / 2, 0.0),
                (width / 2, -depth / 2, 0.0),
            ],
            [
                (corner_center_x, corner_center_y, 0.0),
                (width / 2, corner_center_y, 0.0),
            ],
        ]
        append_surface_patch(floor_patch)

    # -------------------------------------------------------------
    # 5. Mirroring & Winding Order Correction
    # -------------------------------------------------------------
    if settings.preset == 'CORNER' and settings.corner_side == 'RIGHT':
        # Reflect across the X axis; mirror operation inverts normal orientation,
        # so reverse vertex ordering to preserve front-facing normals.
        vertices = [(-x, y, z) for x, y, z in vertices]
        faces = [list(reversed(face)) for face in faces]

    return vertices, faces