"""CORAL's rock crumb (sheet T sprite 171, 1x1: a 7 x 8 lump in the 12 x 14 cell; enemies 1220 and 1222 of episode 5,
the ground layer; one frame, not animated), modelled (2026-10-29; until now it had no model and was drawn flat from its
sprite). models.cfg: model coral_crumb enemies/coral_crumb.glb, sprite t 171 coral_crumb yaw=0 spin=3 (it turns slowly
as it flies, as the flying stones do).

What it is: what CORAL's seahorses spit at the player (polish_coral_seahorse.py): enemy 1205 (T 241, swimming in from
the left facing right) and 1221 (T 203, from the right facing left) launch one every 80 game frames once the level's
event 58 (Set enemy launch) gives them their launch type, 1220 (flying right, (4, 0)) and 1222 (flying left,
(-4, 0)), from just in front of the snout, across the sea floor on the seahorses' ground layer; armour 5, worth 10.
Launched enemies are made by their launchers (catalog.json lists none of them; TYR3D_LOG_SPAWNS prints them as
"appear: ... enemy 1220 sprite 171"), from the clock 1016 on. No other enemy shows the sprite; it is no other sprite's
pixels mirrored, turned or in other ramps.

As the sprite draws it (columns 3-9, rows 3-10): a lump of salmon-red stone (ramp 4, 0x43-0x4b), lit at its upper
left (0x4b at column 5 of row 4), lighter facets right of its middle and at its lower left (0x4a at columns 5 and 8 of
row 6, column 4 and 7 of row 9), darker in a crease from its lower left in towards its middle (0x45 and 0x43 in rows
7-9) and a nick at its top right (0x43 at column 7 of row 4); three stray dark pixels at its rim (0x10, 0xa4, 0xf4)
are left out.

Built as the flying stones are (polish_flying_stone.py: polish_pebbles' machinery, polish_asteroids.py): one convex
block of stone, its footprint's walls rising steeply from the ground, its top's broad facets leaning towards the light
where the sprite is lit (roof planes), a rounded cap of large facets and a few chips off it; the crease cut in as a
narrow V-shaped groove of darker stone, the nick a finer one, and two small pits (a coral rock's pores, bowls cut
into it); the faces the game's camera sees retriangulated evenly and moved a little by smooth noise (weathered stone,
its facets' edges kept sharp). Flat underneath, about 4 pixels high (the game centres ground enemies' models in height
on their layer, as it does the seahorses that spit them). Colours are the sprite's own palette indices: the stone
0x48, the crease 0x43, the nick and the pits 0x44; a little sheen, as the pebbles. Stone gives no light, but every
material glows faintly in its own colour (GLOW, 0.07): CORAL's water is dark, and the side the slanted camera sees away
from the light would read near black. About 1 500 triangles.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 6, 7): column c's left edge is x = c - 6, row r's top edge y = 7 - r. The spec gives pixel
corners (column, row) of the 12 x 14 sprite (polish_pebbles.P() moves them into polish_asteroids' picture).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_T.png), --preview <prefix> (top and 3/4 views).
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
import polish_pebbles as pp  # noqa: E402  (its build() runs only as a script)
from polish_pebbles import P, crack, block  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

NAME = "coral_crumb"
SPRITE = 171
GLOW = 0.07  # the faint glow of every material, in its own palette colour

# The walls (inset, height): steeper than the flying stones' (the crumb is smaller: their slope would leave it low).
OUTER = [(0.0, 0.0), (0.2, 1.4), (0.5, 2.6), (0.95, 3.5), (1.5, 4.2)]
INNER = [(0.0, 0.0), (0.1, 1.8), (0.3, 3.2), (0.6, 4.1), (1.0, 4.7)]

# The outline (row 3 columns 5-7, rows 5-7 out to column 9, rows 6, 8 and 9 in to column 3, row 10 column 4), its steps
# cut through their middles (the block's footprint is their convex hull). One lump: the lit facet at the upper left,
# the top right of the middle, facets falling to the right, the bottom and the lower left; the crease in from the lower
# left edge (row 8.9) to the middle, the nick down from the top right; two pits.
CRUMB = {
    "prefix": NAME, "sprite": SPRITE, "outer": OUTER, "inner": INNER,
    "crack_shade": 0x43, "hairline_shade": 0x44,
    "blocks": [
        block("lump", [(5.0, 3.0), (8.0, 3.0), (8.6, 3.6), (9.4, 4.5), (10.0, 5.4), (10.0, 7.6), (9.4, 8.6),
                       (8.4, 9.6), (7.0, 10.2), (5.4, 10.6), (4.6, 11.0), (3.8, 10.6), (3.1, 9.8), (3.0, 8.6),
                       (3.0, 6.4), (3.6, 5.4), (4.0, 4.4), (4.4, 3.5)],
              [(6.8, 6.6, 4.3, 0.0, 0.0), (5.0, 4.6, 4.0, -0.4, 0.32), (9.0, 6.4, 3.6, 0.48, 0.05),
               (6.4, 9.6, 3.5, 0.05, -0.45), (3.8, 8.6, 3.5, -0.42, -0.18)],
              0x48, (6.5, 6.8, 4.6, 5.2, 7.8, -3.3, 22), chips=3, seed=21),
    ],
    "cracks": {"crease": crack([(3.0, 9.0), (4.7, 8.3), (6.3, 7.6)], 0.5, 0.55, ends=("out", "in"))},
    "hairlines": [crack([(8.3, 3.6), (7.7, 4.8), (7.2, 5.5)], 0.36, 0.4, ends=("out", "in"))],
    "bowls": [(*P(8.4, 7.3), 0.42, 0.3, 0x44), (*P(5.7, 9.4), 0.36, 0.26, 0x44)],
}


def build():
    options = k.args()
    k.reset()
    pa.REACH = pp.REACH
    rock, _ = pa.build_rock(CRUMB)
    pp.finish_materials(rock)
    pal = k.level_palette()
    for mat in rock.data.materials:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Emission Color"].default_value = (*k.srgb(pal[int(mat.name.rsplit("@", 1)[1])]), 1.0)
        bsdf.inputs["Emission Strength"].default_value = GLOW
    parts = triangulate([rock])
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_T.png")
        mk.compare("%s (T %d)" % (NAME, SPRITE), mk.coverage(parts, 12, 14), k.sprite_mask(sheet, SPRITE, large=False))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(mk.outdir(options), NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, size=(12, 14), scale=24, distance=0.45)


if __name__ == "__main__":
    build()
