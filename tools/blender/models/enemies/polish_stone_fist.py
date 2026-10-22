"""BRAINIAC's stone fists (sheet 5 sprites 81 and 83, 2x2: a 21 x 21 stone lying on the cell's diagonal; ground layer;
enemies 527 (81) and 526 (83) of episode 4, seven and twelve of them in BRAINIAC; one frame each, not animated, no
damaged look (dgr 0), armour 20), polished (2026-10-22; they replace wave3_l.py's stone_fist(), a lumpy body over the
sprite's outline collapsed into a few hundred flat facets). models.cfg: model stone_fist / stone_fist_r
enemies/stone_fist.glb, enemies/stone_fist_r.glb and sprite 5 81 stone_fist yaw=0, sprite 5 83 stone_fist_r yaw=0
(the lines as they are: the game centres them in height on the ground enemies' layer, lifting them clear of the
floor).

Two objects, not one of two pieces: 83 is 81 mirrored exactly (column c of the cell is column 23 - c, every palette
index equal), and the levels never put them side by side. Each is an enemy of its own that the level throws in from a
side of the screen, low down (BRAINIAC's event 17, "ground enemy at the bottom": y 190 - 60 or - 90, at 1, 1901, 2001,
2201 to 2401...: 527 (81) at x 300, past the screen's right edge, 526 (83) at x 0, its left edge, each with a link of
its own; 2201, 2251 send 526 alone, 2301 and 2351 two 526 and one 527): 81 flies up the screen and to the left (its
data's move -3, -4), 83 up and to the right (3, -4), slowed by event 20 twenty ticks later, firing for four ticks at
fifty (event 31), sped up again at sixty. They lead with their big end (81's at the upper left, 83's at the upper
right), as fists punch; yaw=0 keeps them so. No other enemy, launched ones included, shows 81 or 83, and they are no
other sprite's pixels turned or in other ramps. Episode 6 takes only BRAINIAC's top layer (GRAVITRON) and its boss
(COLLECTOR): no fist.

As the sprite and its 4x upscale draw 81 (columns and rows of the 24 x 28 cell; greys of ramp 0, a dark red outline
0x70): a fist of faceted grey stone on the diagonal from the upper left (columns 2-18 of rows 2-12) to the lower right
(columns 14-22 of rows 14-22): its big end the knuckles, their top a broad lit face (0x09-0x0e, brightest at columns
10-11 of rows 7-8) under a lit brow along the top edge, their left side dark (0x03-0x05), parted from the top by a
crease (columns 4-6 of rows 6-10, on to columns 9-11 of row 13); at the right a dark notch with a small lit knob in it
(columns 17-21 of rows 9-14: the thumb); under the knuckles, from the crease's end, the middle lump (columns 10-17 of
rows 12-17, mid greys) parted from the dark lower left (by a crease down column 9) and from the bottom strip (the
crease along row 17 to column 12 and down to the bottom edge at column 14); the heel at the lower right (columns
14-22 of rows 14-22), rounded, parted from the thumb by a crease in from the right edge at row 14.

Built as the asteroids' grey rock is (polish_asteroids.py's machinery, as polish_sky_rocks.py's fist of five lumps,
D 43): each lump a convex block over its part of the outline (its walls rising steeply from the floor and curving in,
roof planes leaning towards the light where the sprite lights it, a rounded cap of large facets on the heel and the
middle lump, a few chips), the blocks joined, the creases cut in as V-shaped grooves of dark stone (0x04), the
hairlines finer (0x06), the thumb's knob laid on; the faces the game's camera sees retriangulated evenly and
weathered by smooth noise. Greys are the sprite's own indices (ramp 0: the knuckles 0x0b, the heel 0x0a, the knob
0x0b, the middle 0x07, the thumb's notch 0x05, the dark left side and the bottom 0x04), matte stone; the dark red
outline is the sprite's edge against the floor, not modelled. 83's model is 81's mirrored (x -> -x).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14). The specs give pixel corners (column, row) of the 24 x 28 sprite
(polish_asteroid_lumpy.P() moves them into polish_asteroids' picture). Flat underneath, about 8 pixels high.

Replaces wave3_l.py's stone_fist() (its section "# --- 5 81, 5 83: BRAINIAC's stone fists": stone_fist() and the
model("stone_fist", 81) and model("stone_fist_r", 83) registrations, and the stone_fist, stone_fist_r line of its
docstring) and wave3_l_art.py's FIST (read only by stone_fist()): remove them so that they don't overwrite these
models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png> (each model's
silhouette against its sprite), --preview <prefix> (top and 3/4 views), --only <name,...>.
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroids as pa  # noqa: E402
import polish_asteroid_lumpy as lumpy  # noqa: E402
from polish_asteroid_lumpy import P, crack  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_sky_rocks import block  # noqa: E402  (RockBlock: chips cut against the tops only)

NAME, SPRITE, MIRROR_NAME, MIRROR_SPRITE = "stone_fist", 81, "stone_fist_r", 83
REACH = 0.55           # how far a block reaches across a crease it borders
# The walls (inset, height): steep from the floor, curving in towards the top (the lumps are 4-9 pixels across and
# about 8 high); at a border between blocks, steeper.
OUTER = [(0.0, 0.0), (0.35, 2.2), (1.0, 4.2), (2.0, 5.8), (3.3, 6.9), (5.0, 7.7)]
INNER = [(0.0, 0.0), (0.12, 2.8), (0.38, 5.4), (0.85, 7.0), (1.5, 7.9)]
ROUGHNESS, METALLIC = 0.6, 0.04

# The creases (pixel corners): from the brow down the knuckles' left side to where they meet the others (J1), from
# there to the thumb's notch in the right edge, down column 9, along row 17 and down to the bottom edge, and in from
# the right edge between the thumb and the heel, on (as a border only) to the middle lump's foot.
J1 = (10.5, 13.4)
CRACKS = {
    "cl": crack([(4.5, 4.6), (4.7, 6.4), (5.6, 8.2), (6.6, 10.0), (8.0, 11.7), (9.3, 12.8), J1], 1.1, 1.9),
    "cm": crack([J1, (12.6, 13.0), (14.6, 12.0), (16.4, 11.0), (17.6, 10.2), (18.9, 9.0)], 1.1, 1.9, ("in", "out")),
    "cv": crack([J1, (9.8, 14.6), (9.6, 16.0), (9.7, 17.5)], 0.95, 1.6),
    "cb": crack([(5.3, 17.3), (8.0, 17.6), (10.4, 17.6), (12.4, 18.0), (13.4, 19.0), (14.0, 20.4), (14.5, 22.6)],
                1.05, 1.8, ("out", "out")),
    "ch1": crack([(22.6, 14.1), (20.6, 14.1), (18.4, 14.4)], 1.0, 1.7, ("out", "in")),
    "ch2": crack([(18.4, 14.4), (16.2, 14.7), (14.4, 15.0)], 0.6, 0.6, cut=False),
    "ch3": crack([(14.4, 15.0), (13.4, 16.0), (12.8, 17.2), (12.5, 18.0)], 0.95, 1.5),
}
HAIRLINES = [
    crack([(5.6, 4.4), (7.4, 4.5), (9.0, 5.3), (10.4, 6.5)], 0.6, 0.75),     # the dent under the brow (row 4)
    crack([(16.8, 16.6), (17.6, 18.4), (17.8, 20.4)], 0.38, 0.45),             # a streak on the heel
]

FIST = {
    "prefix": NAME, "sprite": SPRITE, "cracks": CRACKS, "hairlines": HAIRLINES, "outer": OUTER, "inner": INNER,
    "crack_shade": 0x04, "hairline_shade": 0x06,
    "blocks": [
        # The knuckles: the brow along the top edge, the broad lit face under it leaning to the upper left, falling to
        # the thumb's notch and to the middle lump.
        block("knuckles", [(3.0, 2.0), (11.0, 2.0), (12.5, 2.6), (14.0, 3.0), (15.2, 3.5), (16.0, 4.0), (17.0, 5.0),
                           (18.0, 6.2), (18.0, 7.6), (18.9, 9.0)], ["cl", "cm"],
              [(11.0, 7.0, 8.0, -0.14, 0.22), (6.4, 3.6, 7.4, -0.3, 0.55), (15.6, 6.4, 7.2, 0.5, 0.2),
               (12.4, 11.0, 7.0, 0.15, -0.45), (8.0, 8.8, 7.5, -0.5, -0.1)], 0x0b, seed=3),
        # The left side, in shadow: from the top left corner down the left edge to the bottom crease.
        block("left", [(2.4, 2.6), (2.0, 3.6), (2.0, 10.4), (2.5, 11.0), (3.0, 11.4), (3.0, 13.4), (3.6, 14.2),
                       (4.0, 15.0), (4.4, 16.0), (5.0, 16.6), (5.3, 17.3)], ["cl", "cv", "cb"],
              [(4.6, 11.4, 6.2, -0.75, -0.1), (3.6, 6.0, 6.5, -0.8, 0.12), (7.0, 15.0, 5.8, -0.4, -0.55)], 0x04,
              seed=5),
        # The middle lump under the knuckles, rounded.
        block("middle", [], ["cm", "cv", "cb", "ch2", "ch3"], [(12.6, 15.2, 6.3, -0.08, 0.06)], 0x07,
              cap=(12.8, 15.0, 4.0, 3.6, 6.6, -0.4, 18), chips=2, seed=7),
        # The thumb: the dark notch in the right edge, falling away to the right.
        block("thumb", [(18.9, 9.0), (19.5, 8.6), (20.5, 9.5), (21.5, 10.5), (22.0, 11.2), (22.0, 13.6), (22.6, 14.1)],
              ["cm", "ch1"], [(19.6, 11.6, 5.6, 0.45, 0.05), (18.4, 13.4, 5.4, 0.1, -0.45)], 0x05, seed=11),
        # The heel at the lower right: a rounded cap, highest towards its upper left.
        block("heel", [(22.6, 14.1), (23.0, 15.6), (23.0, 19.6), (22.0, 20.6), (20.8, 21.5), (20.2, 22.2), (19.6, 23.0),
                       (15.4, 23.0), (15.0, 22.5), (14.5, 22.6)], ["ch1", "ch2", "ch3", "cb"],
              [(18.0, 17.4, 7.0, -0.22, 0.2), (20.8, 18.8, 6.4, 0.32, -0.1), (16.8, 21.0, 5.8, -0.05, -0.5)], 0x0a,
              cap=(18.0, 17.8, 5.6, 5.4, 7.6, -1.8, 24), seed=13),
        # The bottom strip at the lower left, in shadow.
        block("bottom", [(5.3, 17.3), (6.2, 17.8), (7.4, 18.2), (8.4, 18.8), (9.0, 19.4), (9.6, 20.0), (10.2, 20.6),
                         (10.8, 21.2), (11.4, 21.8), (13.0, 22.0), (14.5, 22.6)], ["cb"],
              [(10.6, 19.6, 5.0, -0.4, -0.5)], 0x04, seed=17),
    ],
    "bowls": [],
    "ridges": [],
    # The thumb's lit knob (pixel corner, radius, height, grey).
    "knobs": [(*P(20.4, 11.6), 0.75, 0.42, 0x0b)],
}


def build_fist(mirror):
    """The fist (one object, triangulated), 83's mirrored."""
    pa.REACH = REACH
    rock, _ = pa.build_rock(FIST)
    lumpy.finish_materials(rock)
    for mat in rock.data.materials:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = ROUGHNESS
        bsdf.inputs["Metallic"].default_value = METALLIC
    rock.data.validate()  # the joined knob leaves a duplicate face
    if mirror:
        rock.data.transform(Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0)))
        rock.data.flip_normals()
        rock.data.update()
    triangulate([rock])
    bpy.context.view_layer.update()
    return rock


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, mirror in ((NAME, SPRITE, False), (MIRROR_NAME, MIRROR_SPRITE, True)):
        if only and name not in only:
            continue
        k.reset()
        rock = build_fist(mirror)
        rock.name = rock.data.name = name
        if "check" in options:
            sheet = options["check"]
            sheet = os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet
            mk.compare("%s (5 %d)" % (name, sprite), mk.coverage([rock], 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, [rock], os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [rock], size=(24, 28), scale=16, distance=0.7)


if __name__ == "__main__":
    build()
