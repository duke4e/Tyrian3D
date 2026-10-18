"""The small turning bronze crystal (sheet 2 sprite 171, 1x1: 12 x 14 pixels) of MINEMAZE, MINES,
TYRIAN, BONUS and WINDY, polished (2026-10-18; it replaces misc.py's flat pyramid).

A kite-shaped crystal: a crown at the top (a light table and crown facets), a thin dark girdle
(the sprite's dark line across row 3) and a long pavilion narrowing to the point at the bottom
(row 13). It has eight broad dark facets round its long axis with a narrow bright facet along each
ridge between them, so from above it shows the sprite's streaks: a bright one down the middle, a
lighter one either side, dark facets between them, all running together at the point; the ridges
are brightest just under the girdle (where the sprite has its glint) and dimmer towards the point,
and every other one is dimmer, so at rest the middle streak outshines those either side of it.

The game rolls the model about its long axis (Blender's Y) with the animation (models.cfg:
roll=frames:<n>), so every cross-section is a regular figure round that axis (on the cell's centre,
half a pixel left of the sprite's drawn middle, so it turns in place) and the crystal looks the
same four times a turn: as it rolls, one bright streak down the middle gives way to two either
side of it and back, and the flat, glossy facets catch the sun in turn, as the sprite's highlights
move across it.

usage: Blender -b --python polish_diamond.py -- [--out <file.glb>] [--preview <prefix>]
       [--sheets <TYR3D_EXTRACT sheets directory>]   (--sheets: print the silhouette overlap)
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

RIDGES = 8
RIDGE_HALF_ANGLE = math.radians(6.5)  # half the angle a ridge's narrow facet spans round the axis

# The crystal from the top down: (band below the ring, y, radius); the point at TIP_Y.
RINGS = [
    ("crown", 6.9, 3.1),
    ("crown", 5.85, 4.75),
    ("girdle", 4.35, 5.55),
    ("pavilion", 3.2, 5.55),
    ("lower", -3.0, 2.6),
]
TIP_Y = -7.1


def angles():
    """The corners of a cross-section, counter-clockwise from +x seen from +Y: each ridge's narrow
    facet spans [ridge - half angle, ridge + half angle]; a ridge points along +x (the outline at
    the sprite's widest) and along +z (the middle streak, towards the camera)."""
    out = []
    for i in range(RIDGES):
        ridge = 2 * math.pi * i / RIDGES
        out += [ridge - RIDGE_HALF_ANGLE, ridge + RIDGE_HALF_ANGLE]
    return out


def build():
    k.reset()
    # Bronze from the sprite's ramp (palette 16-31): broad facets in its mid shades, the ridges and
    # the table in its light ones, the girdle dark; glossy, a little metallic.
    mats = {
        "table": k.material("diamond_table", palette=0x1b, metallic=0.25, roughness=0.15),
        "crown": k.material("diamond_crown", palette=0x17, metallic=0.25, roughness=0.18),
        "crown_ridge": k.material("diamond_crown_ridge", palette=0x1b, metallic=0.25, roughness=0.15),
        "girdle": k.material("diamond_girdle", palette=0x11, metallic=0.25, roughness=0.3),
        "pavilion": k.material("diamond_pavilion", palette=0x15, metallic=0.25, roughness=0.18),
        "lower": k.material("diamond_lower", palette=0x14, metallic=0.25, roughness=0.2),
        "ridge": k.material("diamond_ridge", palette=0x1c, metallic=0.25, roughness=0.14),
        "ridge_dim": k.material("diamond_ridge_dim", palette=0x19, metallic=0.25, roughness=0.14),
        "lower_ridge": k.material("diamond_lower_ridge", palette=0x19, metallic=0.25, roughness=0.16),
        "lower_ridge_dim": k.material("diamond_lower_ridge_dim", palette=0x16, metallic=0.25, roughness=0.16),
    }
    names = list(mats)
    corners = angles()
    n = len(corners)

    vertices, faces, face_mats = [], [], []
    for _, y, radius in RINGS:
        vertices += [(radius * math.cos(a), y, radius * math.sin(a)) for a in corners]
    tip = len(vertices)
    vertices.append((0.0, TIP_Y, 0.0))

    def index(r, s):
        return r * n + s % n

    def ridge_mat(band, s):
        if s % 2 == 1:  # sector s spans corners s and s + 1: even sectors are a ridge's narrow facet
            return band
        if band in ("crown", "girdle"):
            return {"crown": "crown_ridge", "girdle": "girdle"}[band]
        # Down the pavilion every other ridge is dimmer: at rest the middle one (pointing at the
        # camera) and the outline's are bright, the two between dimmer, as in the sprite.
        name = "lower_ridge" if band == "lower" else "ridge"
        return name if (s // 2) % 2 == 0 else name + "_dim"

    faces.append(tuple(index(0, s) for s in range(n)))  # the table, facing up the screen
    face_mats.append("table")
    for r in range(len(RINGS) - 1):
        band = RINGS[r][0]
        for s in range(n):
            faces.append((index(r, s), index(r, s + 1), index(r + 1, s + 1), index(r + 1, s)))
            face_mats.append(ridge_mat(band, s))
    last = len(RINGS) - 1
    for s in range(n):  # the point
        faces.append((index(last, s), index(last, s + 1), tip))
        face_mats.append(ridge_mat(RINGS[last][0], s))

    obj = k.mesh_object("diamond", vertices, faces)
    for name in names:
        obj.data.materials.append(mats[name])
    for poly, name in zip(obj.data.polygons, face_mats):
        poly.material_index = names.index(name)
        poly.use_smooth = False  # crisp facets
    k.recalc_normals(obj)

    options = k.args()
    if "sheets" in options:
        k.check_silhouette(os.path.join(options["sheets"], "enemy_2.png"), 171, large=False)
    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.finish(os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies", "diamond.glb"), size=(12, 14))


build()
