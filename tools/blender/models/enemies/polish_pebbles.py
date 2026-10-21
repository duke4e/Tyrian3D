"""The small blue-grey rocks of the asteroid levels (sheet D sprites 95, 114, 133 and 152, 1x1: 12 x 14 pixels; sky
layer; ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY, AST. CITY, AST ROCK and ASTEROIDS, enemies 317-324 of episodes 1-3
and 1009-1016 of episode 5, two enemy types per rock; one frame each, not animated), polished (2026-10-21; they
replace wave3_j_rocks.py's small_rock() and wave2_f.py's pebble(), glossy lumpy ellipsoids with a shine laid on).
models.cfg: sprite d 95 pebble_a yaw=0, sprite d 114 pebble_b yaw=0, sprite d 133 pebble yaw=0, sprite d 152
pebble_c yaw=0 (the lines as they are).

The four are four different rocks: none is another's pixels turned, mirrored or in other ramps (their outlines are
alike, 0.74-0.94 of each other's at best, but their shades agree in at most 37 % of the pixels), so each has a model
of its own; all four are ramp 6 (blue-grey) with a dark rim of ramp 0 (01, 03) and a near-black outline (20).

As the sprites and their 4x upscales draw them: weathered lumps of blue-grey stone, lit at their upper left, their
sides dark, creased into knobs. D 95 (pebble_a): a rounded rock, a lit knob at the upper left over the
bulk, a crease running in from the left between them. D 114 (pebble_b): a rock lying on the diagonal from the upper
right to the lower left, two knobs along it, a curled crease between them. D 133 (pebble): a rounder, smaller rock
(rows 1-12, columns 0-10), one lump with a bright facet in its middle and a curl of a hairline crack round it.
D 152 (pebble_c): a lumpy rock of three knobs (upper left, right, lower left) between creases meeting in its middle.

Built as the polished big asteroids' blocks are (polish_asteroids.py, whose machinery this uses), but each rock one
stone (knobs of their own read as separate stones at this size): a convex block, its footprint's walls rising
steeply from the ground, its top broad facets lit as the upscale's knobs are (roof planes leaning towards the light
where the sprite is lit), a rounded cap of large facets (the faceted hull of points on an ellipsoid) and a few
chips off it; the creases cut in as narrow V-shaped grooves of dark stone (their course and width wandering a
little), the hairlines finer; the faces the game's camera sees retriangulated evenly and every point moved a little
along its normal by smooth noise: weathered stone, its facets' edges kept sharp. Colours are the sprites' own palette
indices (ramp 6): the stone 0x69, the creases 0x64, the hairlines 0x66, with a little sheen (the upscales' lit facets
shine; the big asteroids are matte); no glow (it is stone). The rocks fly in the sky: flat underneath (the camera
never sees their bellies), 5.5-6.7 pixels high, centred in height by the game.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 6, 7): column c's left edge is x = c - 6, row r's top edge y = 7 - r. The specs below give
pixel corners (column, row) of the 12 x 14 sprite (P() moves them into polish_asteroids' picture).

Replaces wave3_j_rocks.py's small rocks (the "D 95, 114, 152: small rocks (1x1)" section: small_rock() and the three
@model registrations pebble_a(), pebble_b(), pebble_c(), and the pebble_a, pebble_b, pebble_c lines of its docstring;
wave3_j_art.py's D95, D114 and D152, which nothing else reads) and wave2_f.py's pebble() (its "The pebble (sheet
D 133, 1x1)" section with the @model("pebble", "enemy_D", 133, large=False) registration, and the pebble line of its
docstring): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each rock's silhouette
against enemy_D.png), --preview <prefix> (each rock's top and 3/4 views), --only <name,...>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroids as pa  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# How far a block reaches across a crease it borders (the big asteroids' 0.7 is too much for 12 pixels; the rocks
# are one block each, so it only matters if a spec splits one).
REACH = 0.4
# The walls (inset, height): steep from the ground, curving in towards the cap; at a border between blocks, steeper.
OUTER = [(0.0, 0.0), (0.3, 1.6), (0.8, 3.0), (1.6, 4.2), (2.6, 5.0)]
INNER = [(0.0, 0.0), (0.1, 2.2), (0.3, 4.4), (0.7, 5.8), (1.3, 6.6)]
# The stone's sheen (the big asteroids' greys are matte, 0.62).
ROUGHNESS, METALLIC = 0.4, 0.1


def P(c, r):
    """A pixel corner of the 12 x 14 sprite in polish_asteroids' picture (whose px() puts its corner 24, 28 at the
    origin): the sprite's centre (6, 7) at the origin."""
    return (c + 18.0, r + 21.0)


def corners(points):
    return [P(c, r) for c, r in points]


def crack(points, width=0.6, depth=1.0, ends=("in", "in"), cut=True):
    return pa.Crack(corners(points), width, depth, ends, cut)


def block(name, rim, roofs, shade, cap, cracks=(), chips=3, seed=0):
    """A lump of stone: its rim (pixel corners on the outline), its facets (roof planes: column, row, height, nx, ny;
    through that point, leaning as (nx, ny, 1)), its shade, its cap (column, row, rx, ry, rz, z of the ellipsoid's
    centre, points) and the creases it borders."""
    return pa.Block(name, corners(rim), list(cracks), [(*P(c, r), z, nx, ny) for c, r, z, nx, ny in roofs], shade,
                    random_chips=chips, seed=seed, cap=(*P(cap[0], cap[1]), *cap[2:]))


def spec(name, sprite, blocks, cracks, hairlines=(), bowls=()):
    return {"prefix": name, "sprite": sprite, "blocks": blocks, "cracks": cracks, "hairlines": list(hairlines),
            "outer": OUTER, "inner": INNER, "crack_shade": 0x64, "hairline_shade": 0x66,
            "bowls": [(*P(c, r), radius, depth, shade) for c, r, radius, depth, shade in bowls]}


# --- D 95: pebble_a -------------------------------------------------------------------------------------------------
# The outline (rows 0-13; row 0 columns 1-6, rows 4-8 the full width, row 13 columns 2-8), its steps cut through their
# middles. One lump: a broad lit facet at the upper left (the upscale's highlight), the top a little right of the
# middle, facets falling to the right and to the bottom; a crease running in from the left edge (row 8) to the
# middle, under the lit facet, and a hairline at the lower right.

PEBBLE_A = spec("pebble_a", 95, [
    block("lump", [(1.3, 0.0), (6.6, 0.0), (8.5, 0.8), (10.0, 2.2), (11.6, 3.6), (12.0, 4.8), (12.0, 8.8), (11.4, 9.6),
                   (11.0, 11.5), (10.0, 12.8), (8.6, 13.8), (2.4, 13.8), (1.0, 12.6), (0.0, 11.4), (0.0, 1.4),
                   (0.6, 0.4)],
          [(5.6, 6.4, 7.4, 0.0, 0.0), (3.0, 3.4, 6.8, -0.36, 0.3), (6.6, 10.8, 6.3, 0.05, -0.4),
           (9.8, 6.0, 6.2, 0.45, 0.08)],
          0x69, (6.0, 7.0, 8.4, 9.0, 12.4, -4.4, 22), seed=3),
], {
    "c1": crack([(0.0, 8.2), (2.6, 7.6), (5.6, 6.6)], ends=("out", "in")),
}, hairlines=[crack([(8.0, 9.6), (9.4, 11.0), (9.6, 12.6)], 0.4, 0.45)])

# --- D 114: pebble_b ------------------------------------------------------------------------------------------------
# Lying on the diagonal (row 0 columns 5-9 down to row 13 columns 1-7): one lump along it, a lit facet on its upper
# half and a second, lower one on its lower half, the curled crease between them running in from the left edge
# (row 5.8) to the middle; a hairline across its top.

PEBBLE_B = spec("pebble_b", 114, [
    block("lump", [(5.4, 0.0), (9.6, 0.0), (10.6, 0.6), (11.4, 1.5), (12.0, 2.6), (12.0, 10.6), (11.4, 11.5),
                   (10.6, 12.4), (9.0, 13.4), (7.6, 14.0), (1.6, 14.0), (0.4, 13.2), (0.0, 12.2), (0.0, 8.6),
                   (0.6, 7.4), (1.0, 5.6), (1.6, 4.6), (2.6, 3.6), (3.2, 2.4), (4.2, 1.2)],
          [(6.8, 6.6, 7.4, 0.0, 0.0), (6.6, 3.4, 7.0, -0.28, 0.34), (4.0, 9.8, 6.7, -0.36, 0.02),
           (9.6, 9.4, 6.1, 0.38, -0.3)],
          0x69, (6.2, 7.0, 8.6, 9.6, 12.6, -4.6, 22), seed=7),
], {
    "c1": crack([(1.0, 5.8), (3.6, 6.4), (5.4, 7.6), (7.6, 8.4)], ends=("out", "in")),
}, hairlines=[crack([(5.0, 2.4), (6.6, 2.8), (8.4, 2.2)], 0.4, 0.45)])

# --- D 133: pebble --------------------------------------------------------------------------------------------------
# Rounder and smaller (rows 1-12, columns 0-10): one lump, its middle the bright facet; a hairline crack curls round
# its left and bottom (as the upscale's curl), a short one at its right.

PEBBLE = spec("pebble", 133, [
    block("lump", [(1.3, 1.0), (5.6, 1.0), (7.5, 1.9), (9.2, 2.6), (10.3, 3.6), (11.0, 4.8), (11.0, 8.6), (10.3, 9.6),
                   (10.0, 10.6), (9.2, 11.6), (8.2, 12.6), (7.2, 13.0), (2.6, 13.0), (1.4, 12.2), (0.4, 11.0),
                   (0.0, 10.0), (0.0, 2.6), (0.5, 1.6)],
          [(4.6, 6.0, 7.0, -0.3, 0.24), (8.6, 8.4, 5.9, 0.42, -0.2), (5.6, 10.6, 5.9, 0.0, -0.4)],
          0x69, (5.4, 6.8, 7.4, 7.6, 11.4, -3.8, 22), chips=4, seed=13),
], {}, hairlines=[crack([(3.4, 2.8), (2.4, 5.0), (2.6, 7.6), (4.0, 9.4), (6.4, 9.8)], 0.5, 0.6),
                  crack([(7.4, 3.4), (8.6, 5.4), (8.8, 7.2)], 0.4, 0.45)])

# --- D 152: pebble_c ------------------------------------------------------------------------------------------------
# Lumpy (rows 0-13, nearly the full width): three facets lit as the upscale's three highlights (upper left, right
# of the middle, lower left), the creases meeting in the middle (column 7.2, row 6.2): down from the top edge (column
# 6.8) and in from the left edge (row 6.4); a hairline on to the lower right.

PEBBLE_C = spec("pebble_c", 152, [
    block("lump", [(3.4, 0.0), (10.6, 0.0), (11.6, 0.6), (12.0, 1.6), (12.0, 11.6), (11.6, 12.4), (10.8, 13.2),
                   (9.6, 14.0), (2.4, 14.0), (1.2, 13.2), (0.4, 12.4), (0.0, 11.4), (0.0, 5.6), (0.6, 4.4),
                   (1.0, 2.6), (1.6, 1.6), (2.4, 0.8)],
          [(6.8, 7.0, 7.6, 0.0, 0.0), (3.6, 3.0, 7.0, -0.34, 0.3), (9.2, 4.6, 7.1, 0.12, 0.22),
           (4.4, 10.2, 7.0, -0.32, 0.1), (10.2, 10.6, 6.0, 0.4, -0.3)],
          0x69, (6.2, 7.0, 8.4, 9.2, 12.4, -4.4, 24), chips=4, seed=17),
], {
    "a": crack([(6.8, 0.0), (7.0, 3.0), (7.2, 6.2)], ends=("out", "in")),
    "b": crack([(0.0, 6.4), (3.6, 6.6), (7.2, 6.2)], ends=("out", "in")),
}, hairlines=[crack([(7.6, 7.0), (9.6, 9.0), (11.2, 10.4)], 0.45, 0.5)])

SPECS = {"pebble_a": PEBBLE_A, "pebble_b": PEBBLE_B, "pebble": PEBBLE, "pebble_c": PEBBLE_C}


def finish_materials(rock):
    """The big asteroids' greys are matte (roughness 0.62); the pebbles' upscales draw their lit facets glossy: a
    little sheen, broken up by the weathering."""
    for mat in rock.data.materials:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = ROUGHNESS
        bsdf.inputs["Metallic"].default_value = METALLIC


def build_one(s, options):
    k.reset()
    pa.REACH = REACH
    rock, _ = pa.build_rock(s)
    finish_materials(rock)
    parts = triangulate([rock])
    bpy.context.view_layer.update()
    name = s["prefix"]
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_D.png")
        mk.compare("%s (D %d)" % (name, s["sprite"]), mk.coverage(parts, 12, 14),
                   k.sprite_mask(sheet, s["sprite"], large=False))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts, size=(12, 14), scale=24, distance=0.45)


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else list(SPECS)
    for name in only:
        build_one(SPECS[name], options)


if __name__ == "__main__":
    build()
