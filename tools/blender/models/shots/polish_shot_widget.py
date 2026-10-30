"""The Widget Beam's shots (shots sheet sprites 20, 21 and 22, all 1x1: 12 x 14 cells), modelled (2026-10-29, the
second round of the energy shots' models; until then each was drawn as its sprite with volume and the automatic glow).
Built with polish_shot_fireball.py's kit (the pulse's method: half-bodies on the bands' borders, a raised core).

Who fires them: the Widget Beam (front port 40, shop 4:1, 950), straight up the screen at 10 pixels a game frame, a
volley every 2-3 frames (none animated, none turned by heading):
  power  1: 20              power  5: 21 + 20 20 (15 out)      power  9: 22 22 (22 out) + 20 20 (9 out)
  power  2: 20 20 (9 out)   power  6: 21 21 + 20 20 (11 out)   power 10: 22 22 22 22 (16, 22 out) + 20
  power  3: 20 20 (3 out)   power  7: 21 21 + 21 21 (17 out)   power 11: 22 22 22 22 + 20 20
  power  4: 21 + 20 20      power  8: 21 + 22 22 (18 out)
the Tropical Cherry Companion (sidekick 29: two 20s), the Flare and Super Bomb specials (20 in eight ways), and
enemies: weapon 143 (20 and 21: DELI's and New Deli's turrets, CORE's by fire override), 12 (20: SAVARA, SAVARA V,
SAVARA Y, SAVARA IV, APPROACH) and 16 (20 and 21: SAVARA's, by fire override), falling down the screen as drawn.

As the sprites draw them (ramp 7): a pill of yellow-white plasma 5 pixels wide (columns 4-8: its middle half a pixel
right of the cell's), 7 rows long (20, rows 4-10), 9 (21, rows 3-11) or 12 (22, rows 1-12): round ends (the end rows
3 pixels wide, 0x76 0x79 0x76), the row inside them yellow (0x7b 0x7d with orange 0x76/0x78 corners), the rest white
down its three middle columns (0x7f and 0x7e, swapping from row to row: a braid) between bright yellow edges (0x7b at
the rows next to the ends, 0x7d along the middle).

The models: a capsule of plasma, round on top and flat underneath, lofted along the screen's y (polish_shot_fireball.
Loft): its heat rises from the orange of its round ends to the yellow of its body (each band border two rings, one
near each end), its edges a little cooler than its middle; a white spine stands out of its top from end to end (a long
oval: 0x7f in its middle, 0x7e round it), as the sprite's white middle columns.
The same build for the three lengths (shot_widget 20, _2 21, _3 22); 8 materials.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
built on z = 0 (the game centres shot models in height on the player's layer).

models.cfg: see the block's comment (glow= in place of the automatic glow).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_widget.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402

# The bands: (lowest heat, palette index, emission strength), ramp 7 from the ends' orange to the body's yellow.
BANDS = [(-99.0, 0x76, 0.34), (7.6, 0x78, 0.42), (9.0, 0x79, 0.46), (10.4, 0x7b, 0.52), (11.7, 0x7c, 0.56),
         (12.9, 0x7d, 0.58)]
# The spine: (from u, palette index, emission) from its middle out: white in its middle, pale yellow round it.
SPINE_BANDS = ((0.0, 0x7f, 0.62), (0.55, 0x7e, 0.6))
# The capsule: its middle x, half-width, height over half-width, the length of its round ends (pixels); its heat on its
# middle line by the distance from the nearer end (pixels), less towards its edges by the distance from the nearer end;
# the spine's distance from the ends, half-width and lift (an oval standing out of the capsule's top).
X, HALF_WIDTH, DEPTH, CAP = 0.5, 2.5, 0.9, 1.7
ALONG = ((0.0, 7.8), (0.5, 9.6), (1.5, 12.9), (2.5, 14.6), (3.2, 15.0), (99.0, 15.0))
ACROSS = ((0.0, 4.0), (0.6, 5.5), (1.5, 5.5), (2.5, 3.0), (3.2, 2.5), (99.0, 2.5))
SPINE = (1.1, 1.15, 0.32)

# name: (sprite, its first and last row, what it is)
MODELS = [
    ("shot_widget", 20, 4, 10, "a ball of plasma"),
    ("shot_widget_2", 21, 3, 11, "a capsule"),
    ("shot_widget_3", 22, 1, 12, "a tall capsule"),
]


def capsule(name, first, last):
    nose, tail = kit.TOP - first, kit.TOP - last - 1
    length = nose - tail
    along, across = kit.curve(ALONG), kit.curve(ACROSS)

    def end_distance(t):
        return min(t, 1.0 - t) * length

    def width(t):
        d = end_distance(t)
        return HALF_WIDTH * (max(0.0, 1.0 - (1.0 - d / CAP) ** 2) ** 0.5 if d < CAP else 1.0)

    def heat(t, s):
        d = end_distance(t)
        return along(d) - across(d) * min(abs(s), 1.3) ** 2
    mats = kit.materials("widget_plasma", BANDS)
    body = kit.Loft(X, nose, tail, width, heat, BANDS, depth=DEPTH, segments=8, tongues=(3.0, 0.02, 2.3), gap=0.14,
                    width_gap=0.5, head_fractions=(0.1, 0.3, 0.6), tail_fractions=(0.4, 0.7, 0.9))
    parts = [body.build(name + "_plasma", mats)]
    inset, w, lift = SPINE
    spine_mats = kit.materials("widget_spine", SPINE_BANDS, kit.CORE_ROUGHNESS)
    parts.append(kit.dome_core(name + "_spine", (X, (nose + tail) / 2), w, length / 2 - inset, lift, body.top,
                               SPINE_BANDS, spine_mats, segments=16, tongues=(4, 0.0, 1.0)))
    return parts


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", kit.OUTDIR)
    for name, sprite, first, last, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(capsule(name, first, last))
        bpy.context.view_layer.update()
        print(f"== {name} (shots {sprite}): {what}")
        if "check" in options:
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"), [(sprite, 0, 0, 0)], (X, 0.0))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
