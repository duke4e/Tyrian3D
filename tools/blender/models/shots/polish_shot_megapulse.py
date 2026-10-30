"""The Mega Pulse's shot (shots sheet sprites 35, 36, 37 and 38, 1x1: 12 x 14 cells: the four frames of one animated
shot), modelled (2026-10-29, the second round of the energy shots' models; until then each frame was drawn as its sprite
with volume and the automatic glow). Built with polish_shot_fireball.py's kit (the pulse's method: half-bodies on the
bands' borders, a raised core).

Who fires it: the Mega Pulse (front port 19, shop 1:5, 900): one shot straight up the screen at 6 pixels a game frame at
power 1-9 (from power 7 following the ship's x), two (14 apart) at power 10, three at power 11 (the outer two 6 behind);
its damage grows with the power. Its weapons (400-410) have weapani 3, so a player's shot shows four frames, 35 36 37
38, one a game frame, round and round (shots.c: shotAniMax = weapani + 1). No other weapon draws them.

As the sprites draw it (ramp 7): a dripping fireball. Its head a ball 10 pixels wide (columns 1-10, rows 0-8), yellow
in its middle (0x7d in 35, 0x7c in 36 and 38, 0x7b in 37: it flickers), orange round that and a dark red rim; under it
three drips of fire hanging down to row 13: one in the middle (columns 4-7, narrowing to 5-6) and one at either side
(columns 2 and 9), dark gaps between them; a brighter bead runs down the middle drip from frame to frame (0x7a at row 9
in 35, 0x76 at row 11 in 36, 0x74 in 37, gone in 38) and the side drips flicker dark red.

The models (shot_megapulse_35 .. _38, one per frame, as the enemies' animation frames are modelled): the fireball's
head and middle drip one body of fire round on top and flat underneath, lofted along the screen's y
(polish_shot_fireball.build_drop); its heat a field round the head's middle (polish_shot_fireball.blob_heat: the bands
in rings round it, not chevrons), capped down the middle drip by y as the sprite's middle columns; each band border is
two rings of the mesh, before and behind the hot middle; the side drips small lofts of their own (their roots inside
the head); a raised core of yellow on the head's middle (dome_core). The four frames share the outline; their heat is
each frame's (the head's peak, the middle drip's heat with its bead, the side drips'), so the bands move and flicker
from frame to frame as the sprites' do. 9 materials each.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
built on z = 0 (the game centres shot models in height on the player's layer).

models.cfg: see the block's comment.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_megapulse.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402

# The bands: (lowest heat, palette index, emission), ramp 7 from the drips' dark red to the head's yellow.
BANDS = [(-99.0, 0x71, 0.2), (2.0, 0x73, 0.24), (4.0, 0x75, 0.31), (6.0, 0x77, 0.38), (8.0, 0x79, 0.46),
         (9.5, 0x7a, 0.5), (10.7, 0x7b, 0.52)]

# The shape, the same in every frame: the head's tip at row 0's top edge (y 7), the middle drip's at row 13's bottom
# edge (y -7); its half-width (t: 0 the tip, 1 the middle drip's tip); the side drips (x, root y inside the head, tip y,
# half-width); the core's middle, half-axes and lift.
SHAPE = dict(
    nose=7.0, tail=-7.0, depth=0.86, segments=12,
    width=((0.0, 0.0), (0.012, 1.6), (0.036, 2.95), (0.1, 3.95), (0.17, 4.7), (0.25, 4.95), (0.45, 4.95), (0.55, 4.8),
           (0.61, 4.3), (0.65, 3.2), (0.69, 2.45), (0.75, 2.05), (0.82, 1.75), (0.88, 1.1), (0.95, 0.85), (1.0, 0.0)),
    tongue_across=((0.0, 1.0), (1.0, 1.0)),
    waves=(2.5, 0.025, 1.9),
)
SIDE_DRIPS = ((-3.45, 0.2, -7.0, 0.62), (3.45, 0.2, -7.0, 0.62))
CORE = (0.0, 2.0, 2.1, 2.25, 0.32)

# Each frame's heat: the head's (round its middle, 2 above the sprite's centre: half-axes 5 across, 5 up, 6.5 down; the
# head's yellow 0x7d in 35, 0x7c in 36 and 38, 0x7b in 37), never more than the middle drip's down the screen (by y,
# as the sprite's middle columns: the bead of brighter fire running down it); the side drips' along them (root ..
# tip: the root inside the head, the visible part from t 0.3); the core's bands (from its middle out).
HEAD = ((0.0, 13.2), (0.4, 13.0), (0.55, 12.0), (0.7, 10.5), (0.85, 7.5), (1.0, 4.5), (1.15, 2.5), (1.3, 0.5),
        (2.0, 0.2))
FRAMES = {
    35: dict(peak=0.0, drip=((-7.0, 0.2), (-6.5, 0.3), (-5.5, 2.0), (-4.5, 4.0), (-3.5, 7.0), (-2.5, 10.0),
                             (-1.5, 11.0), (-0.5, 99.0)),
             side=((0.0, 8.0), (0.3, 6.0), (0.43, 3.2), (0.57, 2.0), (0.71, 1.0), (0.86, 0.4), (1.0, 0.0)),
             core=((0.0, 0x7d, 0.58), (0.5, 0x7c, 0.56))),
    36: dict(peak=-1.0, drip=((-7.0, 0.3), (-6.5, 0.5), (-5.5, 3.4), (-4.5, 4.8), (-3.5, 5.2), (-2.5, 6.6),
                              (-1.5, 9.2), (-0.5, 99.0)),
             side=((0.0, 7.0), (0.3, 5.0), (0.43, 4.0), (0.57, 2.0), (0.71, 0.3), (0.86, 0.2), (1.0, 0.0)),
             core=((0.0, 0x7c, 0.56), (0.5, 0x7b, 0.52))),
    37: dict(peak=-2.0, drip=((-7.0, 0.6), (-6.5, 1.0), (-5.5, 2.2), (-4.5, 2.4), (-3.5, 2.4), (-2.5, 4.6),
                              (-1.5, 7.4), (-0.5, 99.0)),
             side=((0.0, 5.0), (0.3, 2.6), (0.43, 2.4), (0.57, 2.0), (0.71, 1.0), (0.86, 0.3), (1.0, 0.0)),
             core=((0.0, 0x7c, 0.56), (0.5, 0x7b, 0.52))),
    38: dict(peak=-1.0, drip=((-7.0, 0.1), (-6.5, 0.2), (-5.5, 0.3), (-4.5, 0.6), (-3.5, 1.6), (-2.5, 3.8),
                              (-1.5, 8.4), (-0.5, 99.0)),
             side=((0.0, 5.0), (0.3, 1.8), (0.43, 1.4), (0.57, 1.2), (0.71, 1.0), (0.86, 0.6), (1.0, 0.0)),
             core=((0.0, 0x7c, 0.56), (0.5, 0x7b, 0.52))),
}


def frame_spec(sprite):
    frame = FRAMES[sprite]
    spec = dict(SHAPE)
    head = [(d, h + frame["peak"] * (1.0 - min(d, 1.0) * 0.5)) for d, h in HEAD]
    spec["heat"] = kit.blob_heat((0.0, 2.0), 5.0, 5.0, 6.5, head, frame["drip"])
    spec["tongues"] = [d + (frame["side"],) for d in SIDE_DRIPS]
    spec["tongue_along"] = frame["side"]
    spec["core"] = CORE
    return spec


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", kit.OUTDIR)
    for sprite in FRAMES:
        name = "shot_megapulse_%d" % sprite
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(kit.build_drop(name, frame_spec(sprite), "megapulse", BANDS, FRAMES[sprite]["core"]))
        bpy.context.view_layer.update()
        print(f"== {name} (shots {sprite}): the Mega Pulse's frame")
        if "check" in options:
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"), [(sprite, 0, 0, 0)], CORE[:2])
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
