"""UNDERDELI's white dart turned to fly across the screen (sheet ^, written x5e, sprites 190 and 152, 1x1; enemies 43 and
44 of episode 4, the ground layer), modelled (2026-10-22; until now they had no model and were drawn as flat volumes).

What they are: the brick crab's middle piece (x5e 159, enemies 45 and 47) launches a white dart every 12 game frames
(x5e 171, enemies 41 and 42: white_dart, falling (0, 4)). The dart's launch is "inline with the player" (its elaunchtype
1043 / 1044: launchspecial 1, every game frame): when it comes down to the player's row it launches enemy 43 (45's
darts, from the screen's left) or 44 (47's, from the right) in its place and is gone (its frames 171 999, animate 2:
the launch starts the animation, 999 removes it). 43 flies to the right ((2, -1), its x speed up by 1 every 3 game frames:
xcaccel 3), 44 to the left ((-2, -1), xcaccel -3): with the ground's scroll they streak across the screen at the
player's height, faster and faster. They stay on the dart's layer (ground 2). No other enemy shows these sprites
(catalog.json; enemy 41/42's frames are 171 999).

The sprites are the white dart's pixels turned: x5e 190's pixel (row r, column c) is x5e 171's (row c, column r), the
dart lying across the screen with its nose (the glowing band 0x74 0x78 0x74, column 10, and the body after it, column 11;
the dart's dark point is cut off by the cell's edge) to the right; x5e 152 is 190 mirrored, nose to the left. As the
dart is its own mirror image about its axis, 190 is the dart (as its sprite draws it, nose down) turned 90 degrees
counter-clockwise and moved a pixel right and two up, (x, y) -> (1 - y, 2 + x): its axis at y 1.5 (row 5), its band at
x 4.5, its rear at x -6 (column 0). 152 is 190 turned half round about (0, 1.5).

Built from polish_launched_darts.py's white dart (white_dart(), the 171 colours: the same mesh, materials and band):
white_dart_right (x5e 190) and white_dart_left (x5e 152) are that model placed as their sprites draw it. models.cfg's
yaw cannot do it (the dart's model turned about the sprite's centre would lie 2 pixels low and 1 short of the
sprites), and yaw=velocity would point them up and across (their speed is (x, -1); the ground's scroll keeps them level
on the screen).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r). The game centres the models in height.

models.cfg (new): model white_dart_right enemies/white_dart_right.glb, model white_dart_left enemies/white_dart_left.glb;
sprite x5e 190 white_dart_right yaw=0 glow=6:0.3:120:4.5:-1.5, sprite x5e 152 white_dart_left yaw=0
glow=6:0.3:120:-4.5:-1.5 (the band, as the dart's glow=6:0.3:120:-0.5:3.5).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_x5e.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_darts import white_dart  # noqa: E402

SHEET = "x5e"


def placed(degrees, dx, dy):
    """The dart (built nose up the screen, its axis at x 0.5) turned `degrees` counter-clockwise about its middle and
    moved by (dx, dy)."""
    return Matrix.Translation((dx, dy, 0.0)) @ Matrix.Rotation(math.radians(degrees), 4, "Z")


MODELS = [
    # name, sprite, the dart turned and moved as the sprite draws it: nose up -> right (-90 degrees) and (1, 2) on;
    # nose up -> left (90 degrees) and (-1, 1) on (190's turned half round about (0, 1.5)).
    ("white_dart_right", 190, placed(-90.0, 1.0, 2.0)),
    ("white_dart_left", 152, placed(90.0, -1.0, 1.0)),
]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, matrix in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = white_dart(name, 171)
        mk.transform(objects, matrix)
        triangulate(objects)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_%s.png" % SHEET)
            mk.compare("%s (x5e %d)" % (name, sprite), mk.coverage(objects, 12, 14),
                       k.sprite_mask(sheet, sprite, large=False))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects, size=(12, 14), scale=32, distance=0.42)


if __name__ == "__main__":
    build()
