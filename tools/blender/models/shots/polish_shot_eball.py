"""The enemy's yellow ball (shots sheet sprites 168 and 169, 1x1: 12 x 14 cells), modelled (2026-10-29, round 2 of the
energy shots' models; until then it was drawn as its sprite with volume, flat, from the 4x sheets, with the automatic
glow).

Who fires it: enemy weapon 63 (20 enemy types, aimed at the player: DELI's and New Deli's turrets, ASTEROID2's and AST.
CITY's rocks, TORM's, SOH JIN's, GRYPHON's, BOTANY's and BONUS' guns, IXMUCANE's and SAWBLADES' pods, HARVEST's, SAVARA
IV's, APPROACH's and SAVARA's craft, FLEET's once a fire override event gives them a frequency) and 133 (falling down
the screen at 6: TORM, BOTANY A and B, BONUS, FLEET, STATION), in episodes 1-5. An enemy's shot shows weapani frames
(tyrian2.c: animate cycles below animax = weapani, one step a game frame): weapon 63 has weapani 2, so its ball shows
168 and 169 by turns (it throbs, 35 times a second), weapon 133 weapani 1 (168 only). Round: its lines take no yaw.

As the sprites draw it: 168 a ball 11 pixels across (columns 0-10, rows 1-11: its middle half a pixel left of and
above the cell's centre), white (0x7f) five pixels across in its middle, pale yellow (0x7e) and yellow (0x7d) round
that, its rim yellow-orange (0x7c, 0x7b); 169 the same ball 9 pixels across (columns 1-9, rows 2-10, the same middle),
a shade dimmer (its white three pixels across, its rim 0x7b).

The model: polish_shot_pellet.py's bead (a dome round on top and flat underneath, its bands on rings of the mesh, the
borders waving round it a little, a heart of plasma standing out of its top, leant towards the camera so that the
camera sees the rings where the sprite lays them out) as a ball of light 11 pixels across: ramp 7's yellows out from a
white heart (0x7f round which 0x7e, standing 0.5 pixels proud) through pale yellow and yellow to a thin orange rim
(0x7a, a shade darker than the sprite's 0x7b: a rim that keeps the ball apart from white clouds), every band glowing
(0.46-0.56, the heart 0.6), so the ball reads bright all over from the slanted camera (a ball lit only by the sun
reads near black on its far side). 169 is the same ball 9 pixels across: its rim is the same shade, only its white
middle is relatively smaller, so its line shows this model at scale=0.818 (9/11) rather than a model of its own (no
second set of draws); the ball throbs in size as the sprite does. 524 triangles, 6 materials.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the ball stands on z = 0
(the game centres shot models in height on the player's layer).

models.cfg (the shots section):
    model shot_eball shots/shot_eball.glb
    shot shots 168 shot_eball             glow=15:0.6:125:-0.5:-0.5   # the yellow ball
    shot shots 169 shot_eball scale=0.818 glow=13:0.6:125:-0.5:-0.5   # 9 pixels across (second frame)

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_eball.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from polish_shot_pellet import Bead, bead, materials, run  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The heat out from the middle (u = r / 5.5): the sprite's white out to 2.5 pixels, then 0x7e, 0x7d, the rim.
HEAT = ((0.0, 15.0), (0.42, 15.0), (0.55, 14.0), (0.73, 13.0), (0.9, 12.0), (1.0, 11.0))
RADIUS, HEIGHT = 5.5, 4.2
# Its bands ((lowest heat, palette index, emission), the rim first) and its heart's ((from u, palette index, emission),
# the middle first).
BANDS = [(-99.0, 0x7a, 0.46), (11.6, 0x7b, 0.5), (12.5, 0x7c, 0.53), (13.4, 0x7d, 0.56)]
HEART_BANDS = ((0.0, 0x7f, 0.6), (0.5, 0x7e, 0.6))
HEART = (3.4, 0.5)  # (radius, how far it stands proud of the ball's top)
FLAMES = (7, 0.03, 1.6, 0.12)  # (lobes round it, their reach in u, their turn per border, their swell in pixels)
FIRE_ROUGHNESS, HEART_ROUGHNESS = 0.5, 0.4

MODELS = [
    ("shot_eball", 168, "the yellow ball (169, the second frame: scale=0.818)"),
]


def build_model(name, sprite):
    spec = Bead(-0.5, 0.5, RADIUS, HEIGHT, HEAT, BANDS, (HEART[0] / RADIUS, HEART[0] / RADIUS, HEART[1], HEART_BANDS),
                flames=FLAMES, segments=32, heart_segments=14, heart_rings=(0.35, 0.65, 0.88, 1.0))
    return triangulate(bead(name, spec, materials("eball_fire", spec.bands, FIRE_ROUGHNESS),
                            materials("eball_heart", spec.heart[3], HEART_ROUGHNESS)))


if __name__ == "__main__":
    run(MODELS, build_model)
