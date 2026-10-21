"""The lumpy grey asteroid of the asteroid levels (sheet D sprite 5, 2x2: 24 x 28 pixels, the rock in its columns 2-23
of rows 1-20; sky layer; ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY, AST. CITY, AST ROCK and ASTEROIDS, enemies 135-137
of episodes 1-3 and 5; one frame, not animated), polished (2026-10-21; it replaces wave2_h.py's asteroid_lumpy(), a
noisy icosphere blob pushed out to the sprite's outline, its facets shaded at random). models.cfg: model
asteroid_lumpy enemies/asteroid_lumpy.glb and sprite d 5 asteroid_lumpy yaw=0 (the lines as they are).

D 5 is no other sprite's pixels mirrored, turned or in other ramps, but D 93 (rock_beacon, whose frames 55 and 18
light its lamp) is D 5's pixels with a lamp set into its right (15 pixels differ, columns 17-22 of rows 9-15): the
same rock; ROCK below is its spec, for building that one from this.

As the sprite and its 4x upscale draw it (all in the grey ramp 0, a near-black outline round it): weathered rock lit
from the upper left, broken into four lumps by dark creases: the upper left lump, carved with a ring round a shallow
bowl (columns 8-14 of rows 5-10, its rim lit) and an arc of a curl outside it on its upper left (from column 6 of row
6 over the top to column 13 of row 3: together a swirl, as the big asteroids' glyphs), a lit facet at its left
(columns 5-8 of rows 8-11); the knob at the upper right (columns 14-23 of rows 2-10), its left face brightly lit; the
lump at the bottom (columns 7-15 of rows 11-20), lit along its top, a hairline crease down its middle; the block at
the lower right (columns 15-23 of rows 10-18), darker, falling away to the right, streaked by hairlines.

Built as the polished big asteroids are (polish_asteroids.py, whose machinery this uses, as polish_pebbles.py does):
each lump a convex block (its footprint's walls rising steeply from the ground, roof planes leaning towards the
light where the upscale lights it, a few chips off it; the knob a rounded cap of large facets), the blocks joined,
the creases cut in as V-shaped grooves of dark rock (their course and width wandering a little), the hairlines finer,
the bowl cut out, the ring and the arc laid on as low welts, the faces the camera sees retriangulated evenly and
every point moved a little along its normal by smooth noise: weathered stone, its facets' edges kept sharp. The
creases meet in T-junctions, not a cross (the upscale's lumps are offset), and the lumps' edges along them are
lowered to meet (the swirl's front and the bottom lump's top), so the camera sees a crease there, not a wall. Greys
are the sprite's own palette indices (ramp 0), as the big asteroids': the lumps 0x08-0x0a, the ring 0x0c (the
sprite's brightest), the arc 0x0b, the bowl 0x08, the creases 0x04, the hairlines 0x06; matte stone (roughness 0.58,
a hair glossier than the big asteroids' 0.62: the upscale's lit ring shines a little); no glow. It flies in the sky:
flat underneath (the camera never sees its belly), 9.5 pixels high, centred in height by the game.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r. The specs give pixel
corners (column, row) of the 24 x 28 sprite (P() moves them into polish_asteroids' picture).

Replaces wave2_h.py's asteroid_lumpy (the "D 5: the asteroid" section: ASTEROID, _ray_polygon(), asteroid_lumpy() and
its MODELS entry): asteroid_lumpy is the last model wave2_h.py builds, so wave2_h.py can be deleted (nothing imports
it; wave2_h_kit.py stays: wave3_i_kit.py and wave3_l_kit.py import it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_D.png), --preview <prefix> (top and 3/4 views).
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

NAME, SPRITE = "asteroid_lumpy", 5
# How far a block reaches across a crease it borders (the big asteroids' 0.7, the pebbles' 0.4).
REACH = 0.55
# The walls (inset, height): steep from the ground, curving in towards the top; at a border between blocks, steeper.
OUTER = [(0.0, 0.0), (0.4, 2.4), (1.1, 4.6), (2.2, 6.3), (3.6, 7.3)]
INNER = [(0.0, 0.0), (0.12, 3.0), (0.4, 6.2), (0.9, 8.2), (1.6, 9.2)]
ROUGHNESS, METALLIC = 0.58, 0.03


def P(c, r):
    """A pixel corner of the 24 x 28 sprite in polish_asteroids' picture (whose px() puts its corner 24, 28 at the
    origin): the sprite's centre (12, 14) at the origin."""
    return (c + 12.0, r + 14.0)


def corners(points):
    return [P(c, r) for c, r in points]


def crack(points, width=0.9, depth=1.6, ends=("in", "in"), cut=True):
    return pa.Crack(corners(points), width, depth, ends, cut)


def block(name, rim, cracks, roofs, shade, cap=None, chips=3, seed=0):
    """A lump: its rim (pixel corners on the outline), the creases it borders, its facets (roof planes: column, row,
    height, nx, ny; through that point, leaning as (nx, ny, 1); the first one's point on the lump's own side of its
    creases), its shade, a rounded cap (column, row, rx, ry, rz, z of the ellipsoid's centre, points) or none."""
    return pa.Block(name, corners(rim), list(cracks), [(*P(c, r), z, nx, ny) for c, r, z, nx, ny in roofs], shade,
                    random_chips=chips, seed=seed, cap=None if cap is None else (*P(cap[0], cap[1]), *cap[2:]))


# The outline (rows 1-20, the near-black edge included), its steps cut through their middles. The creases: down from
# the top edge between the swirl and the knob (ab), across from the left edge under the swirl (al) to where they
# meet (J1), on to the right edge under the knob (b1, b2), and down from a point on that (J2) to the bottom edge
# between the bottom lump and the lower right block (lr).
J1, J2 = (15.6, 10.4), (17.2, 10.8)
CRACKS = {
    "ab": crack([(14.0, 1.0), (14.9, 3.4), (14.5, 6.0), (15.1, 8.6), J1], 1.0, 1.9, ("out", "in")),
    "al": crack([(2.0, 11.8), (4.4, 12.2), (7.0, 11.4), (9.8, 11.2), (12.4, 10.7), J1], 0.95, 1.8, ("out", "in")),
    "b1": crack([J1, J2], 0.85, 1.5),
    "b2": crack([J2, (19.6, 10.9), (21.6, 10.2), (24.0, 9.9)], 0.75, 1.3, ("in", "out")),
    "lr": crack([J2, (16.5, 13.2), (16.7, 16.2), (17.4, 18.6)], 0.95, 1.7, ("in", "out")),
}
HAIRLINES = [
    crack([(10.4, 12.8), (11.2, 14.0), (11.6, 15.4), (12.4, 16.8)], 0.42, 0.5),   # down the bottom lump
    crack([(18.6, 12.0), (19.0, 13.6), (19.6, 15.4)], 0.38, 0.45),               # the streaks on the lower right
    crack([(21.0, 11.6), (21.4, 13.0), (22.0, 14.4)], 0.36, 0.42),
    crack([(4.2, 8.2), (5.2, 6.8)], 0.36, 0.42),                                  # on the left lobe's edge
]

ROCK = {
    "prefix": NAME, "sprite": SPRITE, "cracks": CRACKS, "hairlines": HAIRLINES, "outer": OUTER, "inner": INNER,
    "crack_shade": 0x04, "hairline_shade": 0x06,
    "blocks": [
        # The upper left lump: its carved face nearly level, its facets leaning to the upper left (lit) and the left.
        block("swirl", [(2.0, 11.8), (2.0, 6.6), (2.6, 6.0), (3.0, 5.4), (4.0, 4.4), (4.0, 3.4), (5.0, 2.4), (5.6, 1.6),
                        (6.5, 1.0), (14.0, 1.0)], ["ab", "al"],
              [(10.0, 6.4, 9.1, -0.1, 0.08), (7.0, 3.6, 8.5, -0.3, 0.42), (5.0, 9.6, 8.1, -0.5, 0.06),
               (12.8, 9.6, 8.6, 0.16, -0.28), (10.0, 10.6, 7.7, 0.05, -0.45)], 0x0a, seed=3),
        # The knob at the upper right: a rounded cap rising over the swirl, its left face a broad lit facet.
        block("knob", [(14.0, 1.0), (16.5, 1.0), (18.0, 2.0), (20.0, 3.0), (22.0, 4.0), (23.4, 4.6), (24.0, 5.5),
                       (24.0, 9.9)], ["ab", "b1", "b2"],
              [(18.6, 6.2, 9.8, -0.05, 0.05), (16.2, 6.4, 9.2, -0.62, 0.12), (21.6, 8.6, 8.2, 0.4, -0.25)], 0x0a,
              cap=(18.8, 6.0, 6.8, 5.6, 11.8, -2.2, 26), chips=2, seed=5),
        # The bottom lump: rounded, lit along its top, falling away to the bottom.
        block("low", [(2.0, 11.8), (2.4, 12.0), (3.0, 12.4), (4.0, 13.4), (4.0, 14.0), (4.4, 15.4), (5.0, 16.4),
                      (6.0, 17.4), (6.4, 18.4), (7.0, 19.4), (8.0, 20.4), (8.6, 21.0), (15.0, 21.0), (15.6, 20.4),
                      (16.6, 19.6), (17.4, 18.6)], ["al", "b1", "lr"],
              [(11.0, 14.4, 8.7, -0.14, 0.26), (11.0, 12.2, 8.3, -0.1, 0.3), (6.6, 15.2, 7.7, -0.48, -0.12),
               (11.6, 18.6, 7.5, 0.06, -0.5)],
              0x09, cap=(11.0, 14.4, 7.8, 7.0, 11.4, -2.4, 24), seed=7),
        # The block at the lower right: darker and lower, falling away to the right.
        block("right", [(24.0, 9.9), (24.0, 14.6), (23.0, 15.6), (23.0, 16.6), (22.0, 17.4), (19.0, 18.0),
                        (17.4, 18.6)], ["b2", "lr"],
              [(19.6, 13.6, 8.0, 0.12, 0.0), (22.4, 13.0, 7.1, 0.55, 0.1), (20.0, 17.0, 6.9, 0.2, -0.45)],
              0x08, seed=11),
    ],
    # The bowl in the ring (column, row, radius, depth, grey).
    "bowls": [(*P(11.1, 7.7), 1.55, 0.55, 0x08)],
    # The ring round it and the arc of the curl outside it (pixel corners, half width, height, grey).
    "ridges": [
        ([P(12.9, 6.0), P(11.4, 5.0), P(9.6, 5.3), P(8.5, 6.6), P(8.5, 8.4), P(9.5, 9.8), P(11.2, 10.3), P(12.9, 9.6),
          P(13.7, 8.1), P(13.4, 6.6)], 0.95, 0.62, 0x0c),
        ([P(5.9, 6.8), P(6.3, 5.0), P(7.6, 3.6), P(9.6, 2.8), P(11.8, 2.7), P(13.0, 3.2)], 0.8, 0.5, 0x0b),
    ],
    "knobs": [],
}


def finish_materials(rock):
    for mat in rock.data.materials:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = ROUGHNESS
        bsdf.inputs["Metallic"].default_value = METALLIC


def build_rock(spec=ROCK):
    """The rock (one object, triangulated) and its grey materials (polish_asteroids.build_rock with this REACH)."""
    pa.REACH = REACH
    rock, grey = pa.build_rock(spec)
    finish_materials(rock)
    rock.data.validate()  # the joined welts leave a duplicate face
    triangulate([rock])
    bpy.context.view_layer.update()
    return rock, grey


def build():
    options = k.args()
    k.reset()
    rock, _ = build_rock()
    parts = [rock]
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_D.png")
        mk.compare("%s (D %d)" % (NAME, SPRITE), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, SPRITE))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(mk.outdir(options), NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, size=(24, 28), scale=16, distance=0.7)


if __name__ == "__main__":
    build()
