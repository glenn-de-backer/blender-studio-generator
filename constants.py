# SPDX-License-Identifier: GPL-3.0-or-later
"""Stable shape identifiers shared by properties and creation operators."""

# Tuple structure expected by bpy.props.EnumProperty:
# (identifier, name, description, [icon], [number])
PRESETS = [
    (
        'L',
        'L — Back wall',
        'Floor and back wall',
    ),
    (
        'S',
        'S — Front drop',
        'Back wall, floor and downward front lip',
    ),
    (
        'U',
        'U — Opposing walls',
        'Floor between opposing walls',
    ),
    (
        'C',
        'C — Ceiling',
        'Floor, back wall and ceiling',
    ),
    (
        'CORNER',
        'Corner — Adjacent walls',
        'Floor and two adjacent walls',
    ),
]